# System Architecture - Visual Diagrams

## 1. Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          END USER (Browser)                                │
│                                                                             │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │ (Port 8501)
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    STREAMLIT DASHBOARD (Frontend)                          │
│                                                                             │
│  ┌─────────────┬──────────┬─────────────┬──────────┬──────────┬──────┐   │
│  │    Home     │ Details  │   Search    │ Compare  │Analytics│Config│   │
│  └──────┬──────┴─────┬────┴──────┬──────┴─────┬────┴──────┬───┴─────┘   │
│         │ Real-time  │ Search    │Multi-code  │ Trends    │ Health     │   │
│         │KPIs        │Filtering  │Comparison  │Analytics  │Check      │   │
│  ┌──────▼────────────▼───────────▼────────────▼───────────▼─────────┐   │
│  │           API Client (HTTP Requests to FastAPI)                  │   │
│  └──────┬─────────────────────────────────────────────────────────┬─┘   │
│         │ JSON Responses                                          │     │
└─────────┼──────────────────────────────────────────────────────────┼─────┘
          │
          │ REST API Calls
          │ (Port 8000)
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    FASTAPI BACKEND (Web Server)                           │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                        15+ REST Endpoints                         │   │
│  │                                                                    │   │
│  │  Health │ List  │ Details │ Export │ Import │ Stats │ Search    │   │
│  │ Search  │ Compare │ Countries │ Aggregations                     │   │
│  └────┬─────────────────────────────────────────────────────────┬───┘   │
│       │ Pydantic Validation & Serialization                     │       │
│  ┌────▼─────────────────────────────────────────────────────────▼───┐   │
│  │              PyMongo Driver (Database Client)                │   │
│  └────┬────────────────────────────────────────────────────────┬──┘   │
└──────┼────────────────────────────────────────────────────────┼───────┘
       │ TCP Protocol (Port 27017)                            │
       │ BSON Format Queries/Responses                        │
       ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    MONGODB DATABASE (Data Store)                          │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Collections:                                                        │  │
│  │  • hs_codes - Main trade data (10,000+ documents)                   │  │
│  │  • partner_countries - Country-specific details                     │  │
│  │                                                                      │  │
│  │  Indexes:                                                            │  │
│  │  • hs_code (unique) - Fast lookups                                  │  │
│  │  • trade_mode - Filter by export/import                             │  │
│  │  • scraped_at_ist - Time-range queries                              │  │
│  │  • metadata.data_completeness_percent - Quality filtering           │  │
│  │  • (hs_code, country) - Country lookups                             │  │
│  │                                                                      │  │
│  │  Storage Engine: WiredTiger (default)                               │  │
│  │  Compression: Enabled                                               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Pipeline

```
1. SOURCE DATA
   │
   ├─ data/processed/2026-01-21/
   │  └─ HS_61091000.json
   │  └─ HS_84135010.json
   │  └─ ... (1000+ files)
   │
   └─ data/raw/2026-01-21/
      └─ (backup/original data)


2. DATA LOADER (data_loader/loader.py)
   │
   ├─ Read JSON Files
   │  └─ DirectoryTraversal → FileList
   │
   ├─ Validate Records
   │  └─ Pydantic Models → SchemaValidation
   │
   ├─ Check Duplicates
   │  └─ HS Code + Trade Mode → Upsert Decision
   │
   └─ Database Insert
      └─ Bulk Insert (100 records/sec)


3. MONGODB STORAGE
   │
   ├─ Collection: hs_codes
   │  ├─ Document: {hs_code, trade_mode, metadata, data_by_year}
   │  ├─ Index: hs_code (unique)
   │  ├─ Index: trade_mode
   │  └─ Index: metadata.data_completeness_percent
   │
   └─ Automatic Indexing on Connection


4. FASTAPI API LAYER
   │
   ├─ GET /api/hs-codes
   │  └─ Query: {limit=100, skip=0, trade_mode=export}
   │  └─ Response: List[HSCodeSummary]
   │
   ├─ GET /api/hs-codes/{code}
   │  └─ Query: {hs_code=61091000}
   │  └─ Response: HSCodeRecord (complete)
   │
   ├─ POST /api/search
   │  └─ Query: {hs_code, trade_mode, min_completeness}
   │  └─ Response: {count, data}
   │
   └─ GET /api/statistics
      └─ Aggregation: Sum, Avg, Count
      └─ Response: Statistics (KPIs)


5. STREAMLIT FRONTEND
   │
   ├─ Page: Home
   │  └─ HTTP GET /api/statistics → Display KPIs
   │
   ├─ Page: Details
   │  └─ User Input (HS Code) → HTTP GET /api/hs-codes/{code}
   │  └─ Display Complete Data + Charts
   │
   ├─ Page: Search
   │  └─ User Input (filters) → HTTP POST /api/search
   │  └─ Display Results + Export CSV
   │
   └─ Page: Compare
      └─ User Input (codes) → HTTP GET /api/compare
      └─ Display Comparison Charts


6. USER INTERACTION
   │
   ├─ View Dashboard
   ├─ Search by HS Code
   ├─ Apply Filters
   ├─ Export Results
   └─ Analyze Data
```

## 3. Database Schema

```
MongoDB Collection: hs_codes
├─ _id: ObjectId (auto-generated)
├─ hs_code: String (unique index) ✓ INDEXED
├─ trade_mode: String ("export" | "import") ✓ INDEXED
├─ metadata: Object
│  ├─ product_label: String
│  ├─ data_completeness_percent: Number ✓ INDEXED
│  ├─ unique_partner_countries: Number
│  ├─ total_records_captured: Number
│  ├─ years_available: Array[Number]
│  ├─ page_load_time_ms: Number
│  ├─ successful_extractions: Number
│  ├─ extraction_success_rate: Number
│  ├─ scraped_at_ist: String ✓ INDEXED
│  └─ data_validation_errors: Number
└─ data_by_year: Array[Object]
   └─ [0..n]
      ├─ year: Number
      └─ partner_countries: Array[Object]
         └─ [0..n]
            ├─ country: String
            ├─ export_value: Number
            ├─ import_value: Number
            ├─ growth_percent: Number
            └─ quantity: Number


Index Strategy:
─────────────────

1. hs_code (unique=true)
   → Fast lookup: O(1) for single HS code
   → Prevents duplicates
   → Used by: GET /api/hs-codes/{code}

2. trade_mode
   → Filter by export/import: O(1) + data fetch
   → Used by: GET /api/hs-codes?trade_mode=export

3. metadata.data_completeness_percent
   → Range queries: O(log n)
   → Used by: POST /api/search with min_completeness

4. scraped_at_ist
   → Time-range queries: O(log n)
   → Used by: GET /api/hs-codes?from_date=...

5. Composite: (hs_code, trade_mode)
   → Implicit via unique hs_code + queries
```

## 4. API Request-Response Flow

```
User Action: Search HS Code
│
▼
Streamlit: st.text_input("Enter HS Code")
│
▼
User Enters: "61091000"
│
▼
Streamlit: requests.get(
    "http://localhost:8000/api/hs-codes/61091000"
)
│
▼
FastAPI Route:
GET /api/hs-codes/{hs_code}
│
├─ Extract: hs_code = "61091000"
├─ Query: collection.find_one({"hs_code": "61091000"})
├─ Validate: HSCodeRecord(**doc)
└─ Response: {
     "hs_code": "61091000",
     "trade_mode": "export",
     "metadata": {...},
     "data_by_year": [...]
   }
│
▼
Streamlit: Receive Response
│
├─ Parse JSON
├─ Extract fields
├─ Display metadata cards
├─ Generate charts
└─ Show partner countries

Total Time: ~100-200ms
```

## 5. Performance Characteristics

```
DATABASE OPERATIONS
─────────────────

Simple Query (indexed):
  Query: db.hs_codes.find_one({hs_code: "61091000"})
  Time: ~10-50ms
  
List Query (paginated):
  Query: db.hs_codes.find({}).skip(0).limit(100)
  Time: ~50-100ms
  
Aggregation Query:
  Query: db.hs_codes.aggregate([...])
  Time: ~100-500ms
  
Full Scan (no index):
  Query: db.hs_codes.find({...})
  Time: ~500ms-1s


API RESPONSE TIMES
──────────────────

Simple Endpoint:
  GET /api/hs-codes/{code}
  Total: ~50-100ms
  ├─ Network: ~5-10ms
  ├─ FastAPI Processing: ~10-20ms
  ├─ Database Query: ~20-50ms
  └─ JSON Serialization: ~5-10ms

Search Endpoint:
  POST /api/search
  Total: ~100-200ms
  ├─ Network: ~5-10ms
  ├─ FastAPI Processing: ~20-30ms
  ├─ Database Query: ~50-100ms
  └─ JSON Serialization: ~20-30ms

Aggregation Endpoint:
  GET /api/statistics
  Total: ~200-500ms
  ├─ Network: ~5-10ms
  ├─ FastAPI Processing: ~20-30ms
  ├─ Database Aggregation: ~150-400ms
  └─ JSON Serialization: ~20-40ms


STREAMLIT DASHBOARD
───────────────────

Page Load:
  Initial Load: ~1-2s
  ├─ Streamlit Initialization: ~300-500ms
  ├─ API Calls: ~200-500ms per endpoint
  └─ Rendering: ~500-1000ms

Chart Rendering:
  Plotly Chart: ~200-500ms
  Pie/Bar Chart: ~100-300ms

CSV Export:
  Generation: ~100-200ms
  Download: ~50-100ms
```

## 6. Deployment Architecture

```
Development Environment:
────────────────────────

Local Machine
├─ MongoDB (localhost:27017)
├─ FastAPI (localhost:8000)
├─ Streamlit (localhost:8501)
└─ Data Files (local disk)


Production Environment (Recommended):
────────────────────────────────────

┌─────────────────────────────────────┐
│    Load Balancer (nginx)            │
│    Port 80/443 (HTTP/HTTPS)         │
└──────────────────┬──────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐    ┌────────┐    ┌────────┐
│FastAPI │    │FastAPI │    │FastAPI │
│Instance│    │Instance│    │Instance│
│:8000   │    │:8000   │    │:8000   │
└────┬───┘    └────┬───┘    └────┬───┘
     │             │             │
     └─────────────┼─────────────┘
                   │
              ┌────▼────┐
              │MongoDB  │
              │ Cluster │
              │ (3-5    │
              │ nodes)  │
              └─────────┘
              
For Streamlit:
┌──────────────────────────────┐
│  Streamlit Cloud or Server   │
│  Port 443 (HTTPS)            │
│  → Connects to FastAPI       │
└──────────────────────────────┘
```

## 7. Scaling Strategy

```
Current (Single Machine):
────────────────────────
Users: ~10-50 concurrent
QPS: ~100-500 requests/second
Data: 10,000 HS codes
Setup: 1 FastAPI + 1 MongoDB


Scaling: Phase 1 (Multi-API):
──────────────────────
Users: ~100-500 concurrent
QPS: ~1000-5000 requests/second
Setup:
  ├─ Load Balancer (nginx)
  ├─ 3x FastAPI Instances
  ├─ 1x MongoDB (increased RAM)
  └─ Redis Cache Layer


Scaling: Phase 2 (Distributed):
───────────────────────
Users: ~1000+ concurrent
QPS: ~5000+ requests/second
Setup:
  ├─ CDN for Static Assets
  ├─ Load Balancer with Health Checks
  ├─ 5-10x FastAPI Instances
  ├─ MongoDB Replica Set (3 nodes)
  ├─ MongoDB Sharding (for 1M+ records)
  └─ Redis Cluster for Caching
```

## 8. Error Handling Flow

```
HTTP Request
│
▼
FastAPI Middleware
├─ Check request format
└─ Validate headers


Route Handler
│
▼
Input Validation (Pydantic)
├─ Valid? → Continue
└─ Invalid? → Return 422 Unprocessable Entity


Database Operation
│
├─ Success?
│  └─ Return data with 200 OK
│
├─ Not Found?
│  └─ Return 404 Not Found
│
├─ Connection Error?
│  └─ Return 503 Service Unavailable
│
└─ Query Error?
   └─ Return 500 Internal Server Error


Response Serialization
│
├─ Valid Pydantic Model? → JSON
└─ Invalid? → 500 Error


HTTP Response
│
└─ Status Code + JSON Body
   (or error response)
```

## 9. Component Interaction Matrix

```
                 │ Streamlit │ FastAPI │ MongoDB │ Pydantic
─────────────────┼───────────┼─────────┼─────────┼──────────
Streamlit        │     -     │  HTTP   │    -    │    -
FastAPI          │     -     │    -    │ PyMongo │ Validation
MongoDB          │     -     │    -    │    -    │    -
Pydantic         │   Models  │ Models  │    -    │    -
```

## 10. Technology Stack Layers

```
Layer 4: Presentation (User Interface)
┌─────────────────────────────────────┐
│  Streamlit Dashboard (6 Pages)      │
│  - Plotly Charts                    │
│  - Pandas DataFrames                │
│  - Form Inputs                      │
└─────────────────────────────────────┘

Layer 3: Application (Business Logic)
┌─────────────────────────────────────┐
│  FastAPI Backend                    │
│  - 15+ REST Endpoints               │
│  - Request Routing                  │
│  - Response Serialization           │
└─────────────────────────────────────┘

Layer 2: Data Access (ORM/Driver)
┌─────────────────────────────────────┐
│  PyMongo Driver                     │
│  - Query Construction               │
│  - Connection Management            │
│  - Result Parsing                   │
└─────────────────────────────────────┘

Layer 1: Data Storage (DBMS)
┌─────────────────────────────────────┐
│  MongoDB Database                   │
│  - Collections (hs_codes, etc)      │
│  - Indexes                          │
│  - Aggregation Pipeline             │
└─────────────────────────────────────┘
```

---

**Created**: January 2026
**Version**: 1.0
**Status**: Complete ✅
