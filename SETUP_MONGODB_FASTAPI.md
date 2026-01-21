# MongoDB + FastAPI + Streamlit Stack Setup Guide

## Overview

This guide walks you through setting up and running the production-grade trade statistics platform with MongoDB backend, FastAPI REST API, and Streamlit dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Streamlit Dashboard (Port 8501)                │
│  - Multi-page interface (Home, Details, Search, Comparison)     │
│  - Real-time analytics and KPIs                                  │
│  - Advanced filtering and querying                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    HTTP Requests
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                    │
│  - REST API endpoints for data access                           │
│  - Search, filter, compare functionality                        │
│  - Statistics and analytics aggregation                         │
│  - CORS enabled for Streamlit communication                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    PyMongo Driver
                         │
┌────────────────────────▼────────────────────────────────────────┐
│            MongoDB (Port 27017, localhost)                      │
│  - hs_codes collection (main data)                              │
│  - partner_countries collection (country-specific data)         │
│  - Automatic indexes on hs_code, trade_mode, completeness       │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. MongoDB Installation

**Windows:**
```powershell
# Download from https://www.mongodb.com/try/download/community
# Run installer and select "Install as a Service"
# Verify installation
mongod --version

# Start MongoDB service
net start MongoDB

# Test connection
mongosh "mongodb://localhost:27017"
```

**Using Docker (Alternative):**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. Python Dependencies

```bash
# Install required packages
pip install fastapi uvicorn pymongo pydantic pandas streamlit plotly requests

# Or use requirements.txt
pip install -r requirements.txt
```

### 3. Create `requirements.txt`

```
fastapi==0.104.1
uvicorn==0.24.0
pymongo==4.6.0
pydantic==2.5.0
pandas==2.1.0
streamlit==1.28.0
plotly==5.17.0
requests==2.31.0
python-dotenv==1.0.0
```

## Step-by-Step Setup

### Step 1: Verify MongoDB Connection

```bash
# Test MongoDB is running
python -c "
from api.database import get_db
db = get_db()
if db.health_check():
    print('✓ MongoDB is healthy')
else:
    print('✗ MongoDB connection failed')
"
```

### Step 2: Load Data into MongoDB

```bash
# Run the data loader
python -m data_loader.loader

# This will:
# - Read all JSON files from data/processed/
# - Read all JSON files from data/raw/ (fallback)
# - Validate each record with Pydantic models
# - Insert/update records in MongoDB
# - Create necessary indexes
# - Display summary statistics
```

**Expected Output:**
```
Loading PROCESSED data from C:\...\data\processed
Found XXX JSON files in ...
Progress: 10/XXX | Loaded: 15, Updated: 0, Failed: 0
...
DATA LOADING SUMMARY
============================================================
Total Loaded:    XXX
Total Updated:   0
Total Failed:    0
Total Skipped:   0
Total Records:   XXX

DATABASE VERIFICATION:
Total records in MongoDB: XXX
  Export records: XXX
  Import records: XXX
```

### Step 3: Start FastAPI Backend

```bash
# Option 1: Development mode with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Test the API:**
```bash
# Check health
curl http://localhost:8000/health

# List HS codes
curl http://localhost:8000/api/hs-codes?limit=10

# Get statistics
curl http://localhost:8000/api/statistics
```

**API Documentation:**
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

### Step 4: Start Streamlit Dashboard

**In a new terminal:**

```bash
# Run the Streamlit app
streamlit run dashboard/app.py

# Or specify a different port
streamlit run dashboard/app.py --server.port 8501
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501

  Press CTRL+C to quit
```

The dashboard will automatically open in your default browser.

## API Endpoints Reference

### Health Check
- `GET /health` - Check API and database health

### HS Code Management
- `GET /api/hs-codes` - List all HS codes (paginated)
  - Query params: `trade_mode`, `limit`, `skip`
- `GET /api/hs-codes/{hs_code}` - Get detailed data for a specific HS code
- `GET /api/hs-codes/{hs_code}/export` - Get export data only
- `GET /api/hs-codes/{hs_code}/import` - Get import data only

### Statistics
- `GET /api/statistics` - Get overall statistics

### Search
- `POST /api/search` - Advanced search with filters
  - Payload: `{hs_code, trade_mode, min_completeness, max_results}`

### Comparison
- `GET /api/compare` - Compare multiple HS codes
  - Query params: `codes` (comma-separated), `trade_mode`

### Partner Countries
- `GET /api/partner-countries` - Get all partner countries
  - Query params: `country` (filter), `limit`

## Dashboard Pages

### 1. Home
- Real-time KPIs (HS codes count, records, completeness)
- Data quality metrics
- Mode distribution chart
- Completeness gauge

### 2. HS Code Details
- Search for specific HS code
- Display complete metadata
- Yearly data summary
- Top partner countries with visualizations

### 3. Search & Filter
- Advanced search with multiple filters
- Min completeness threshold
- Download results as CSV
- Paginated results display

### 4. Comparison
- Compare multiple HS codes side-by-side
- Completeness comparison chart
- Partner countries comparison
- Trade mode analysis

### 5. Analytics
- Export vs Import distribution
- Data quality analysis
- Overall statistics dashboard
- Insights and trends

### 6. Settings
- API configuration status
- Health check button
- Cache information
- Dashboard information

## Troubleshooting

### MongoDB Connection Issues

**Problem:** "Failed to connect to MongoDB"
```
Solution:
1. Check MongoDB is running:
   mongosh "mongodb://localhost:27017"

2. Verify connection string in api/database.py
   Default: mongodb://localhost:27017

3. Check firewall allows port 27017
```

### FastAPI Port Already in Use

**Problem:** "Address already in use"
```
Solution:
# Use a different port
uvicorn api.main:app --port 8001

# Or kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Streamlit Connection Error

**Problem:** "Failed to fetch statistics" in dashboard
```
Solution:
1. Verify FastAPI is running on http://localhost:8000
2. Check API health: curl http://localhost:8000/health
3. Check firewall allows port 8000
4. Ensure CORS is enabled in FastAPI (already configured)
```

### Data Not Appearing

**Problem:** Dashboard shows empty data
```
Solution:
1. Run data loader:
   python -m data_loader.loader

2. Verify data in MongoDB:
   mongosh
   > use tradestat
   > db.hs_codes.countDocuments()

3. Check loader output for errors
```

## Optimization Tips

### 1. Faster Data Loading
```bash
# For large datasets, create compound indexes before loading
# Already handled in api/database.py _setup_indexes()
```

### 2. API Performance
```python
# Use pagination to avoid loading all records
GET /api/hs-codes?limit=100&skip=0
GET /api/hs-codes?limit=100&skip=100  # Next page
```

### 3. Dashboard Caching
```python
# Cache is set to 5 minutes by default
@st.cache_data(ttl=300)
def get_statistics():
    ...
    
# Use "Refresh Data" button to clear cache
```

## Production Deployment

### 1. Environment Variables
```bash
# Create .env file
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=tradestat
FASTAPI_ENV=production
LOG_LEVEL=INFO
```

### 2. Docker Deployment

```dockerfile
# Dockerfile for FastAPI
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t tradestat-api .
docker run -p 8000:8000 --link mongodb tradestat-api
```

### 3. Running Multiple Workers
```bash
# Production-grade FastAPI with Gunicorn + Uvicorn
pip install gunicorn

gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Monitoring

### 1. Check Data Quality
```bash
python -c "
from api.database import get_db
db = get_db()
stats = db.get_collection('hs_codes').aggregate([
    {'\$group': {
        '_id': '\$trade_mode',
        'count': {'\$sum': 1},
        'avg_completeness': {'\$avg': '\$metadata.data_completeness_percent'}
    }}
])
for item in stats:
    print(item)
"
```

### 2. Monitor API Requests
```python
# Add to api/main.py for request logging
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    return response
```

## Next Steps

1. **Automate Data Updates**: Integrate with daily_scheduler.py to auto-load new data
2. **User Authentication**: Add JWT tokens to API endpoints
3. **Advanced Analytics**: Create new dashboard pages for trend analysis
4. **Alert System**: Set up notifications for data quality issues
5. **Caching Layer**: Add Redis for API response caching
6. **React Frontend**: Replace Streamlit with React for more control

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `data/logs/`
3. Check MongoDB logs
4. Verify all services are running

---

**Last Updated**: January 2026
**Version**: 1.0.0
