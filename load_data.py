import json
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime

def transform_raw_data(raw_data):
    """Transform raw JSON data to match HSCodeRecord schema"""
    
    # Extract from metadata - works for both formats
    metadata = raw_data.get("metadata", {})
    hs_code = metadata.get("hs_code", "")
    
    # Try multiple field names for trade mode
    trade_mode = metadata.get("trade_mode") or metadata.get("trade_type")
    if trade_mode:
        trade_mode = trade_mode.lower()
    
    if not hs_code or not trade_mode:
        return None
    
    # Extract years data
    data_by_year = {}
    years_available = []
    all_countries = set()
    total_data_points = 0
    
    for year_key, year_data in raw_data.get("data_by_year", {}).items():
        data_by_year[year_key] = year_data
        years_available.append(year_key)
        
        # Count countries and data points
        partners = year_data.get("partner_countries", [])
        for partner in partners:
            country = partner.get("Country") or partner.get("country")
            if country:
                all_countries.add(country)
                total_data_points += 1
    
    # Get product label from first year
    product_label = ""
    for year_data in data_by_year.values():
        product_label = year_data.get("product_label", "")
        if product_label:
            break
    
    # Data completeness = 100% (all available data for the scraped date)
    completeness = 100.0
    
    # Build metadata
    transformed_metadata = {
        "hs_code": hs_code,
        "trade_mode": trade_mode,
        "report_type": metadata.get("report_type", "Commodity-wise"),
        "data_frequency": metadata.get("data_frequency", "Annual").lower(),
        "currency": metadata.get("currency", "USD"),
        "quantity_unit": metadata.get("quantity_unit", "NOS"),
        "source_site": metadata.get("source_site", "https://tradestat.commerce.gov.in"),
        "scraped_at_ist": metadata.get("scraped_at_ist", ""),
        "scrape_duration_seconds": metadata.get("scrape_duration_seconds", 0.0),
        "total_records_captured": total_data_points,
        "complete_records": total_data_points,
        "data_completeness_percent": completeness,
        "years_available": sorted(years_available),
        "number_of_years": len(years_available),
        "unique_partner_countries": len(all_countries),
        "page_load_time_ms": 0.0,
        "pipeline_version": metadata.get("pipeline_version", "1.0.0"),
        "controller_version": metadata.get("controller_version", "1.0.0"),
        "scraper_environment": "production",
        "hs_hierarchy": metadata.get("hs_hierarchy", {
            "chapter": "",
            "heading": "",
            "sub_heading": "",
            "hs_8": hs_code
        }),
        "data_currency_unit": metadata.get("currency", "USD"),
        "data_availability_note": f"Complete data available for {len(years_available)} years with {len(all_countries)} partner countries",
        "product_label": product_label
    }
    
    return {
        "hs_code": hs_code,
        "trade_mode": trade_mode,
        "metadata": transformed_metadata,
        "data_by_year": data_by_year,
        "raw_data": raw_data
    }


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["tradestat"]
collection = db["hs_codes"]

# Clear existing data
collection.delete_many({})

# Load data ONLY from today (2026-01-21)
today = datetime.now().strftime("%Y-%m-%d")

# Check both export and import directories for today's data
export_dir = Path(f"data/raw/export/{today}")
import_dir = Path(f"data/raw/import/{today}")
raw_today_dir = Path(f"data/raw/{today}")

data_dirs = []
if raw_today_dir.exists():
    data_dirs.append(raw_today_dir)
if export_dir.exists():
    data_dirs.append(export_dir)
if import_dir.exists():
    data_dirs.append(import_dir)

if not data_dirs:
    print(f"⚠️  No data directories found for today ({today})!")
    print(f"Checked paths:")
    print(f"  - {raw_today_dir.absolute()}")
    print(f"  - {export_dir.absolute()}")
    print(f"  - {import_dir.absolute()}")
    exit(1)

loaded = 0
failed = 0
import_count = 0
export_count = 0
loaded_hs_codes = set()

print(f"Loading data from TODAY ({today})...\n")

for data_dir in data_dirs:
    print(f"Loading from: {data_dir.absolute()}\n")
    
    for json_file in sorted(data_dir.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Transform data
            transformed = transform_raw_data(raw_data)
            
            if transformed:
                hs_code = transformed["hs_code"]
                trade_mode = transformed['trade_mode']
                
                # Use update_one with upsert to handle duplicates from multiple directories
                try:
                    collection.update_one(
                        {"hs_code": hs_code, "trade_mode": trade_mode},
                        {"$set": transformed},
                        upsert=True
                    )
                    loaded += 1
                    if trade_mode == 'export':
                        export_count += 1
                    elif trade_mode == 'import':
                        import_count += 1
                    
                    loaded_hs_codes.add(hs_code)
                    
                    print(f"✓ {json_file.name:<30} HS: {hs_code:<12} Mode: {trade_mode:<8} Countries: {transformed['metadata']['unique_partner_countries']:<4} Years: {transformed['metadata']['number_of_years']}")
                except Exception as db_error:
                    if "duplicate key" in str(db_error):
                        # Skip silently - already loaded from another directory
                        print(f"⊘ {json_file.name:<30} HS: {hs_code:<12} Mode: {trade_mode:<8} (already loaded)")
                    else:
                        raise
            else:
                failed += 1
                print(f"✗ {json_file.name:<30} - Invalid data structure")
                
        except Exception as e:
            failed += 1
            print(f"✗ {json_file.name:<30} - {str(e)[:60]}")

print(f"\n{'='*80}")
print(f"Results: {loaded} loaded, {failed} failed")
print(f"  - Export Records: {export_count}")
print(f"  - Import Records: {import_count}")
print(f"  - Unique HS Codes: {len(loaded_hs_codes)}")
print(f"Total documents in MongoDB: {collection.count_documents({})}")

# Show sample data
print(f"\n{'='*80}")
print("Loaded Documents:")
for doc in collection.find().sort("hs_code", 1):
    mode = doc.get('trade_mode')
    hs = doc.get('hs_code')
    countries = doc.get('metadata', {}).get('unique_partner_countries')
    years = doc.get('metadata', {}).get('number_of_years')
    completeness = doc.get('metadata', {}).get('data_completeness_percent')
    product = doc.get('metadata', {}).get('product_label', 'N/A')
    
    print(f"\n✓ HS Code: {hs} | Mode: {mode.upper():<6} | Product: {product[:50]}")
    print(f"  Partner Countries: {countries} | Years: {years} | Data Completeness: {completeness:.1f}%")
