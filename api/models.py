"""
Pydantic models for data validation and API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class HSHierarchy(BaseModel):
    """HS Code hierarchy breakdown"""
    chapter: str
    heading: str
    sub_heading: str
    hs_8: str


class Metadata(BaseModel):
    """Trade data metadata"""
    hs_code: str
    trade_mode: str
    report_type: str
    data_frequency: str
    currency: str
    quantity_unit: str
    source_site: str
    
    # Timestamps
    scraped_at_ist: str
    scrape_duration_seconds: float
    
    # Data quality
    total_records_captured: int
    complete_records: int
    data_completeness_percent: float
    years_available: List[str]
    number_of_years: int
    unique_partner_countries: int
    
    # Performance
    page_load_time_ms: float
    
    # Versioning
    pipeline_version: str
    controller_version: str
    scraper_environment: str
    
    # HS Code info
    hs_hierarchy: HSHierarchy
    data_currency_unit: str
    data_availability_note: str


class PartnerCountry(BaseModel):
    """Partner country trade data"""
    country: Optional[str] = None
    export_value: Optional[float] = None
    import_value: Optional[float] = None
    growth_percent: Optional[float] = None
    quantity: Optional[float] = None
    

class YearData(BaseModel):
    """Yearly trade data"""
    year: str
    product_label: Optional[str] = None
    partner_countries: List[PartnerCountry] = []
    summary: Optional[Dict[str, Any]] = None
    total_pages: int = 0


class HSCodeRecord(BaseModel):
    """Complete HS Code record"""
    hs_code: str
    trade_mode: str
    metadata: Metadata
    data_by_year: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "hs_code": "61091000",
                "trade_mode": "export",
                "metadata": {
                    "hs_code": "61091000",
                    "trade_mode": "export"
                }
            }
        }


class HSCodeSummary(BaseModel):
    """Summary of HS Code"""
    hs_code: str
    trade_mode: str
    product_label: Optional[str] = None
    data_completeness_percent: float
    unique_partner_countries: int
    years_available: List[str]
    scraped_at_ist: str


class HSCodeSummary(BaseModel):
    """Summary of HS Code data (for list views)"""
    hs_code: str
    trade_mode: str
    product_label: Optional[str] = None
    data_completeness_percent: float
    unique_partner_countries: int
    years_available: List[int]
    scraped_at_ist: str


class SearchFilter(BaseModel):
    """Search and filter parameters"""
    hs_code: Optional[str] = None
    trade_mode: Optional[str] = None
    partner_country: Optional[str] = None
    min_completeness: Optional[float] = 0
    max_results: Optional[int] = 100


class Statistics(BaseModel):
    """Overall statistics"""
    total_hs_codes: int
    export_records: int
    import_records: int
    avg_data_completeness: float
    total_records_captured: int
    unique_countries: int
    years_covered: List[str]
    last_scrape_time: str


class ComparisonResult(BaseModel):
    """Comparison between multiple HS codes"""
    hs_codes: List[str]
    trade_mode: str
    comparison: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
