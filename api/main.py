"""
FastAPI backend for trade data API.
Provides REST endpoints for accessing scraped trade data from MongoDB.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from api.database import init_db, get_db, close_db
from api.models import (
    HSCodeRecord, HSCodeSummary, Statistics, SearchFilter,
    ComparisonResult, ErrorResponse
)
from utils.logger import get_logger

logger = get_logger("FASTAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown"""
    # Startup
    logger.info("Starting FastAPI server...")
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down FastAPI server...")
    close_db()


app = FastAPI(
    title="Trade Statistics API",
    description="API for accessing India's trade data by HS Code",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== HEALTH CHECK =====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db = get_db()
    if db.health_check():
        return {"status": "healthy", "database": "connected"}
    else:
        raise HTTPException(status_code=503, detail="Database connection failed")


# ===================== HS CODE ENDPOINTS =====================

@app.get("/api/hs-codes", response_model=List[HSCodeSummary])
async def list_hs_codes(
    trade_mode: Optional[str] = Query(None, description="Filter by trade_mode: export/import"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    skip: int = Query(0, ge=0, description="Number of records to skip")
):
    """
    List all HS codes with optional filters.
    
    Query parameters:
    - trade_mode: Filter by 'export' or 'import'
    - limit: Max records to return (default: 100)
    - skip: Offset for pagination
    """
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        
        query = {}
        if trade_mode:
            query["trade_mode"] = trade_mode
        
        cursor = collection.find(query).skip(skip).limit(limit)
        results = []
        
        for doc in cursor:
            results.append(HSCodeSummary(
                hs_code=doc["hs_code"],
                trade_mode=doc["trade_mode"],
                product_label=doc.get("metadata", {}).get("product_label"),
                data_completeness_percent=doc.get("metadata", {}).get("data_completeness_percent", 0),
                unique_partner_countries=doc.get("metadata", {}).get("unique_partner_countries", 0),
                years_available=doc.get("metadata", {}).get("years_available", []),
                scraped_at_ist=doc.get("metadata", {}).get("scraped_at_ist", "")
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error listing HS codes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hs-codes/{hs_code}", response_model=HSCodeRecord)
async def get_hs_code(
    hs_code: str,
    trade_mode: Optional[str] = Query(None, description="Filter by export/import")
):
    """
    Get complete data for a specific HS code.
    
    Path parameters:
    - hs_code: The HS code (e.g., 61091000)
    
    Query parameters:
    - trade_mode: Optional filter for 'export' or 'import'
    """
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        
        query = {"hs_code": hs_code}
        if trade_mode:
            query["trade_mode"] = trade_mode
        
        doc = collection.find_one(query)
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"HS code {hs_code} not found")
        
        # Remove MongoDB ID
        doc.pop("_id", None)
        return HSCodeRecord(**doc)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting HS code {hs_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hs-codes/{hs_code}/export")
async def get_hs_code_export(hs_code: str):
    """Get export data for a specific HS code"""
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        doc = collection.find_one({"hs_code": hs_code, "trade_mode": "export"})
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Export data for HS code {hs_code} not found")
        
        doc.pop("_id", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hs-codes/{hs_code}/import")
async def get_hs_code_import(hs_code: str):
    """Get import data for a specific HS code"""
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        doc = collection.find_one({"hs_code": hs_code, "trade_mode": "import"})
        
        if not doc:
            raise HTTPException(status_code=404, detail=f"Import data for HS code {hs_code} not found")
        
        doc.pop("_id", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== STATISTICS ENDPOINTS =====================

@app.get("/api/statistics", response_model=Statistics)
async def get_statistics():
    """Get overall statistics about the dataset"""
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        
        total_docs = collection.count_documents({})
        export_count = collection.count_documents({"trade_mode": "export"})
        import_count = collection.count_documents({"trade_mode": "import"})
        
        # Calculate averages
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_completeness": {"$avg": "$metadata.data_completeness_percent"},
                    "total_records": {"$sum": "$metadata.total_records_captured"},
                    "unique_countries": {"$sum": "$metadata.unique_partner_countries"}
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        stats = results[0] if results else {}
        
        # Get all unique years
        all_years = set()
        for doc in collection.find({}, {"metadata.years_available": 1}):
            all_years.update(doc.get("metadata", {}).get("years_available", []))
        
        return Statistics(
            total_hs_codes=total_docs,
            export_records=export_count,
            import_records=import_count,
            avg_data_completeness=round(stats.get("avg_completeness", 0), 2),
            total_records_captured=stats.get("total_records", 0),
            unique_countries=stats.get("unique_countries", 0),
            years_covered=sorted(list(all_years)),
            last_scrape_time=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== SEARCH ENDPOINTS =====================

@app.post("/api/search")
async def search_hs_codes(filter: SearchFilter):
    """
    Search HS codes with advanced filters.
    
    Filters:
    - hs_code: Specific HS code
    - trade_mode: 'export' or 'import'
    - partner_country: Search by country name
    - min_completeness: Minimum data completeness %
    - max_results: Maximum results to return
    """
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        
        query = {}
        if filter.hs_code:
            query["hs_code"] = {"$regex": filter.hs_code}
        if filter.trade_mode:
            query["trade_mode"] = filter.trade_mode
        if filter.min_completeness and filter.min_completeness > 0:
            query["metadata.data_completeness_percent"] = {"$gte": filter.min_completeness}
        
        cursor = collection.find(query).limit(filter.max_results or 100)
        results = []
        
        for doc in cursor:
            doc.pop("_id", None)
            results.append(doc)
        
        return {"count": len(results), "data": results}
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== COMPARISON ENDPOINTS =====================

@app.get("/api/compare")
async def compare_hs_codes(
    codes: str = Query(..., description="Comma-separated HS codes to compare"),
    trade_mode: Optional[str] = Query(None, description="export or import")
):
    """
    Compare multiple HS codes.
    
    Example: /api/compare?codes=61091000,03061710&trade_mode=export
    """
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        
        code_list = [c.strip() for c in codes.split(",")]
        query = {"hs_code": {"$in": code_list}}
        
        if trade_mode:
            query["trade_mode"] = trade_mode
        
        docs = list(collection.find(query))
        
        if not docs:
            raise HTTPException(status_code=404, detail="No matching HS codes found")
        
        comparison = {}
        for doc in docs:
            doc.pop("_id", None)
            comparison[doc["hs_code"]] = {
                "trade_mode": doc["trade_mode"],
                "completeness": doc["metadata"]["data_completeness_percent"],
                "countries": doc["metadata"]["unique_partner_countries"],
                "years": doc["metadata"]["years_available"]
            }
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing codes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================== PARTNER COUNTRY ENDPOINTS =====================

@app.get("/api/partner-countries")
async def get_partner_countries(
    country: Optional[str] = Query(None, description="Filter by country name"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all partner countries in the dataset.
    
    Optional filter by country name.
    """
    try:
        db = get_db()
        collection = db.get_collection("hs_codes")
        
        pipeline = [
            {"$unwind": "$data_by_year"},
            {"$unwind": "$data_by_year.partner_countries"},
            {"$group": {
                "_id": "$data_by_year.partner_countries.country",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        if country:
            pipeline.insert(2, {"$match": {
                "data_by_year.partner_countries.country": {"$regex": country, "$options": "i"}
            }})
        
        results = list(collection.aggregate(pipeline))
        return {"countries": results}
    except Exception as e:
        logger.error(f"Error getting partner countries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
