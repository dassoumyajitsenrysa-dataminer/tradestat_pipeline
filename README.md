# Trade Statistics Platform - India Export/Import Dashboard

A professional, enterprise-grade analytics dashboard for India's trade statistics with comprehensive HS code analysis, country-level drill-downs, and strategic growth insights.

## 🎯 Features

### Home Page
- **India Context**: Clear country branding and reporting date
- **Trade Composition**: Export vs Import breakdown with percentages
- **Market Coverage**: Number of countries, HS codes, and years of data
- **Data Quality Metrics**: Completeness gauge and status

### HS Code Details - 3 Analysis Modes

#### 1. **Overview Analysis**
- Business KPIs (Product, Partners, Historical Data, Data Quality)
- Performance Metrics (Current Value, Active Partners, CAGR, 7-Year Growth)
- Multi-tab trend analysis:
  - Value Trends (line chart)
  - Partner Expansion (area chart)
  - YoY Growth Rates (bar chart)
- Top 15 Trading Partners with market share breakdown
- Market share pie chart

#### 2. **Country Drill-Down**
- Interactive country selector
- Metrics: Current Value, Average, 7-Year Growth, Trend Direction
- Timeline visualization (India → Country trade over 7 years)
- Year-over-year growth analysis
- Detailed transaction table

#### 3. **Growth Analysis**
- Total trade value trends
- Market concentration risk tracking
- Partner expansion metrics
- Strategic recommendations based on data
- World map with geographic distribution
- New market entry analysis

### Additional Pages
- **Search & Filter**: Advanced HS code search with export capabilities
- **Comparison**: Compare multiple HS codes side-by-side
- **Analytics**: Market overview with export/import analysis
- **Settings**: API configuration and system diagnostics

## 📊 Data

- **HS Codes**: 13 commodity codes (12 Export + 1 Import)
- **Partner Countries**: Up to 214 countries per HS code
- **Historical Data**: 7 years (2018-2025)
- **Data Date**: 2026-01-21
- **Completeness**: 100% for latest date

## 🔧 Technical Stack

- **Backend**: FastAPI (Port 8000)
- **Frontend**: Streamlit (Port 8502)
- **Database**: MongoDB (localhost:27017)
- **Visualizations**: Plotly
- **Data Processing**: Pandas, NumPy
- **Python Version**: 3.13+

## 📋 Prerequisites

- Python 3.10+
- MongoDB (running locally on port 27017)
- Streamlit Account (for cloud deployment)
- GitHub Account (for Streamlit Cloud)

## 🚀 Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MongoDB
```bash
# Windows
mongod

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### 3. Load Initial Data
```bash
python load_data.py
```

### 4. Start FastAPI Backend
```bash
python api/main.py
```

### 5. Run Streamlit Dashboard
```bash
streamlit run dashboard/app.py --server.port=8502
```

Access at: `http://localhost:8502`

## 🌐 Streamlit Cloud Deployment (Private Access)

### Step 1: Prepare GitHub Repository
```bash
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial trade statistics dashboard"

# Create a new repository on GitHub (https://github.com/new)
# Copy repository URL

# Push to GitHub
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

### Step 2: Create Streamlit Cloud Account
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your GitHub repository
5. Select main branch
6. Set Main file path to: `dashboard/app.py`

### Step 3: Configure for Private Access

#### Option A: Password Protection (Recommended)
Create `.streamlit/secrets.toml`:
```toml
# Password protect the app
[credentials]
password = "your-secure-password-here"
```

Then update `dashboard/app.py` to add at the top of `main()`:
```python
import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        # Form to enter a password
        with st.form("password_form"):
            password = st.text_input("Enter Dashboard Password", type="password")
            if st.form_submit_button("Login"):
                if password == st.secrets["credentials"]["password"]:
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

# Rest of your dashboard code...
```

#### Option B: Streamlit Sharing Settings
1. In Streamlit Cloud dashboard, click on your app's three-dot menu
2. Select "Settings"
3. Under "Sharing Settings", set to "Private" (visible only to you and invited users)
4. Add your manager's email in the share settings

#### Option C: Environment Variable Protection
Create `.streamlit/secrets.toml`:
```toml
[database]
mongo_uri = "your-mongodb-atlas-uri"
api_key = "your-api-key"

[app]
secret_key = "your-secret-key"
```

### Step 4: Configure Environment Variables

In Streamlit Cloud dashboard settings, add:
```
MONGO_URI = "your-mongodb-atlas-connection-string"
API_BASE_URL = "http://your-api-server:8000"
```

### Step 5: Share Link with Manager

Once deployed:
1. Your app URL: `https://share.streamlit.io/your-username/tradestat_pipeline/main/dashboard/app.py`
2. Share only this link with your manager
3. If using password protection, share the password separately via secure channel
4. If using Streamlit Sharing privacy, add manager's email to permissions

## 🔐 Security Best Practices

1. **Never commit secrets**: Keep `secrets.toml` in `.gitignore`
2. **Use MongoDB Atlas**: Don't expose local MongoDB credentials
3. **API Authentication**: Implement JWT tokens for API endpoints
4. **Password Protection**: Use strong, unique passwords
5. **HTTPS Only**: Streamlit Cloud uses HTTPS by default
6. **Share Selectively**: Only share links with authorized users

## 📁 Project Structure

```
tradestat_pipeline/
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── api/
│   └── main.py                # FastAPI backend
├── load_data.py               # Data loading script
├── requirements.txt           # Python dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml          # (NOT committed) Secrets
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 📞 Support

For issues or questions:
1. Check Streamlit logs in Cloud dashboard
2. Review MongoDB connection settings
3. Verify API is running and accessible
4. Check browser console for frontend errors

## 📈 Usage Tips

1. **Search & Filter**: Use partial HS code matching (e.g., "610" finds all 61xxx codes)
2. **Drill-Down**: Select any country to see bilateral trade trends
3. **Growth Analysis**: Monitor concentration risk and new market opportunities
4. **Export Data**: Download filtered results as CSV
5. **Comparisons**: Compare multiple HS codes to identify patterns

## 🔄 Data Updates

Currently loads data from `2026-01-21`. To update with new data:
```bash
python load_data.py
```

## ⚡ Performance Notes

- Dashboard caches API responses for 5 minutes
- Large visualizations (1000+ data points) may take 2-3 seconds to render
- World map loads dynamically only when needed
- Database queries optimized with indexing

## 📝 License

Internal Use Only - Confidential

---

**Last Updated**: 2026-01-21
**Version**: 1.0.0
