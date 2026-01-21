# MongoDB + FastAPI + Streamlit - Deployment Checklist

## 📋 Pre-Deployment Checklist

### Phase 1: Environment Setup
- [ ] **MongoDB Installation**
  - [ ] Download and install MongoDB Community Edition
  - [ ] OR use Docker: `docker run -d -p 27017:27017 mongo`
  - [ ] Verify connection: `mongosh "mongodb://localhost:27017"`
  - [ ] Create data directory if needed: `mkdir C:\data\db`
  
- [ ] **Python Setup**
  - [ ] Python 3.9+ installed: `python --version`
  - [ ] Virtual environment created: `python -m venv venv`
  - [ ] Virtual environment activated: `venv\Scripts\activate` (Windows)
  - [ ] Pip upgraded: `python -m pip install --upgrade pip`

- [ ] **Dependencies Installation**
  - [ ] Install all packages: `pip install -r requirements.txt`
  - [ ] Verify installations: `python verify_setup.py`
  - [ ] All checks should show ✓

### Phase 2: Configuration
- [ ] **MongoDB Configuration**
  - [ ] Connection string verified: `MONGO_URL = "mongodb://localhost:27017"`
  - [ ] Database name set: `MONGO_DB_NAME = "tradestat"`
  - [ ] Indexes will auto-create on first connection

- [ ] **FastAPI Configuration**
  - [ ] API port set: `8000` (or custom)
  - [ ] Host configured: `0.0.0.0` for production
  - [ ] CORS enabled for cross-origin requests

- [ ] **Streamlit Configuration**
  - [ ] API base URL set: `http://localhost:8000`
  - [ ] Cache TTL configured: `300` seconds
  - [ ] Page refresh strategy defined

### Phase 3: Data Preparation
- [ ] **Data Availability**
  - [ ] JSON files exist in `data/processed/` directory
  - [ ] OR JSON files exist in `data/raw/` directory
  - [ ] File format validated (valid JSON)
  - [ ] Schema matches Pydantic models

- [ ] **Data Validation**
  - [ ] Run: `python -m data_loader.loader`
  - [ ] Review output for errors
  - [ ] Check database: `db.hs_codes.countDocuments()`
  - [ ] Verify record sample: `db.hs_codes.findOne()`

### Phase 4: Service Launch
- [ ] **MongoDB Service**
  - [ ] Service is running
  - [ ] Health check passes: `mongosh`
  - [ ] Port 27017 is accessible
  - [ ] Connection pooling enabled

- [ ] **FastAPI Backend**
  - [ ] Service starts without errors
  - [ ] Listens on port 8000
  - [ ] Health endpoint works: `curl http://localhost:8000/health`
  - [ ] Swagger docs accessible: `http://localhost:8000/docs`
  - [ ] Database connects successfully

- [ ] **Streamlit Dashboard**
  - [ ] Service starts without errors
  - [ ] Listens on port 8501
  - [ ] Accessible at `http://localhost:8501`
  - [ ] API connectivity verified (no errors in sidebar)
  - [ ] All pages load correctly

### Phase 5: Functional Testing
- [ ] **Home Page**
  - [ ] KPI metrics display correctly
  - [ ] Charts render without errors
  - [ ] Completeness gauge shows value
  - [ ] Distribution charts visible

- [ ] **HS Code Details**
  - [ ] Search bar works
  - [ ] Returns results for valid codes
  - [ ] Metadata displays completely
  - [ ] Charts display correctly

- [ ] **Search & Filter**
  - [ ] HS code search works
  - [ ] Trade mode filter works
  - [ ] Completeness slider works
  - [ ] CSV export generates file

- [ ] **Comparison**
  - [ ] Multiple codes can be entered
  - [ ] Comparison results display
  - [ ] Charts render correctly

- [ ] **API Testing**
  - [ ] Test endpoint: `/health`
  - [ ] Test endpoint: `/api/hs-codes`
  - [ ] Test endpoint: `/api/statistics`
  - [ ] Test endpoint: `/api/search`
  - [ ] Test endpoint: `/api/compare`

### Phase 6: Performance Validation
- [ ] **Response Times**
  - [ ] API responses < 200ms average
  - [ ] Page loads < 2 seconds
  - [ ] Charts render < 500ms
  - [ ] No timeout errors

- [ ] **Data Integrity**
  - [ ] All HS codes loaded correctly
  - [ ] Export/Import records separate
  - [ ] Metadata complete for all records
  - [ ] No data corruption

- [ ] **Resource Usage**
  - [ ] Memory usage reasonable (~200-300MB)
  - [ ] CPU usage low in idle state
  - [ ] No memory leaks observed
  - [ ] Database connections managed

### Phase 7: Backup & Recovery
- [ ] **Database Backup**
  - [ ] Backup procedure documented
  - [ ] Backup schedule defined
  - [ ] Restore procedure tested
  - [ ] Backup storage configured

- [ ] **Configuration Backup**
  - [ ] Settings documented
  - [ ] Connection strings saved
  - [ ] Credentials managed securely

### Phase 8: Monitoring Setup
- [ ] **Logging Configuration**
  - [ ] Logs enabled for all components
  - [ ] Log rotation configured
  - [ ] Log directory monitored

- [ ] **Health Monitoring**
  - [ ] Database health checks scheduled
  - [ ] API health endpoint monitored
  - [ ] Alert threshold defined

- [ ] **Performance Monitoring**
  - [ ] Query performance tracked
  - [ ] API response times logged
  - [ ] Dashboard usage analytics

### Phase 9: Security Hardening (Production Only)
- [ ] **Authentication**
  - [ ] API authentication enabled
  - [ ] JWT tokens configured
  - [ ] User management setup

- [ ] **Network Security**
  - [ ] Firewall rules configured
  - [ ] HTTPS/SSL enabled
  - [ ] Port access restricted

- [ ] **Data Security**
  - [ ] Database encryption enabled
  - [ ] Sensitive data masked in logs
  - [ ] Access control lists defined

### Phase 10: Documentation
- [ ] **User Documentation**
  - [ ] Dashboard usage guide created
  - [ ] API documentation accessible
  - [ ] FAQ compiled

- [ ] **Operational Documentation**
  - [ ] Startup procedure documented
  - [ ] Shutdown procedure documented
  - [ ] Troubleshooting guide ready
  - [ ] Maintenance schedule defined

## 🚀 Quick Start Commands

### One-Command Deployment
```bash
python quick_start.py
```

### Manual Step-by-Step
```bash
# 1. Verify setup
python verify_setup.py

# 2. Load data (in project directory)
python -m data_loader.loader

# 3. Terminal 1: Start FastAPI
uvicorn api.main:app --reload --port 8000

# 4. Terminal 2: Start Streamlit
streamlit run dashboard/app.py

# 5. Open browser
http://localhost:8501
```

## 🔍 Verification Commands

### Health Checks
```bash
# MongoDB
mongosh "mongodb://localhost:27017" --eval "db.admin.command('ping')"

# FastAPI
curl http://localhost:8000/health

# Database content
mongosh
> use tradestat
> db.hs_codes.countDocuments()
> db.hs_codes.findOne()
```

### Data Validation
```bash
# Count records
mongosh
> db.hs_codes.countDocuments({"trade_mode": "export"})
> db.hs_codes.countDocuments({"trade_mode": "import"})

# Check completeness
> db.hs_codes.aggregate([{
  $group: {
    _id: null,
    avg_completeness: {$avg: "$metadata.data_completeness_percent"}
  }}])
```

## 📞 Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| MongoDB won't connect | Check service running, verify connection string |
| Port 8000 in use | Use different port or kill existing process |
| FastAPI crashes | Check logs, verify database connection |
| Dashboard shows errors | Check FastAPI health endpoint |
| No data visible | Run data loader, verify MongoDB has data |
| Slow performance | Check indexes created, use pagination |

## 📊 Post-Deployment Validation

### Success Indicators
- ✅ Home page displays KPIs correctly
- ✅ HS code search returns results
- ✅ Comparison feature works with multiple codes
- ✅ CSV export generates valid file
- ✅ API /docs page is accessible
- ✅ All database queries execute < 200ms
- ✅ No errors in browser console
- ✅ No connection timeouts

### Performance Baselines (Expected)
- API Response: 50-200ms
- Dashboard Load: 1-3 seconds
- Chart Render: 200-500ms
- Database Query: 10-100ms
- Search Results: <500ms

## 📈 Scaling Checklist (For 10,000+ HS Codes)

- [ ] MongoDB indexes verified for hs_code, trade_mode, completeness
- [ ] Pagination implemented on all list endpoints
- [ ] Caching strategy implemented (Redis/Memcached)
- [ ] FastAPI configured with multiple workers
- [ ] Load balancer configured for multi-server setup
- [ ] Database replication configured
- [ ] Read replicas created for analytics queries
- [ ] Backup strategy automated

## 🔒 Security Checklist (For Production)

- [ ] Database authentication enabled
- [ ] API authentication (JWT) implemented
- [ ] CORS restricted to known domains
- [ ] HTTPS/SSL certificates installed
- [ ] Firewall rules restrict port access
- [ ] Database connections encrypted
- [ ] Sensitive data not logged
- [ ] Rate limiting implemented
- [ ] SQL injection prevention (already done with Pydantic)
- [ ] CSRF protection enabled

## 📅 Maintenance Schedule

### Daily
- [ ] Monitor error logs
- [ ] Check API response times
- [ ] Verify database connectivity

### Weekly
- [ ] Review performance metrics
- [ ] Check backup completion
- [ ] Test disaster recovery

### Monthly
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Update dependencies (if patches available)

### Quarterly
- [ ] Major version updates
- [ ] Capacity planning review
- [ ] Architecture evaluation

## ✅ Sign-Off Checklist

Before considering deployment complete:

- [ ] All tests passed
- [ ] Performance meets expectations
- [ ] Documentation complete
- [ ] Team trained on operation
- [ ] Backup verified
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Management approval obtained

---

**Deployment Date**: _______________
**Deployed By**: _______________
**Approved By**: _______________
**Notes**: _______________

**Status**: Ready for Deployment ✅
