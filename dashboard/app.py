"""
Advanced multi-page Streamlit dashboard connected to FastAPI backend.
Provides comprehensive analytics and querying capabilities for trade data.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

# Configure dashboard
st.set_page_config(
    page_title="Trade Statistics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
import os
from pymongo import MongoClient

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# MongoDB connection (for direct access)
try:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    mongo_client.server_info()  # Test connection
    db = mongo_client["tradestat"]
    MONGO_AVAILABLE = True
except:
    MONGO_AVAILABLE = False
    db = None

# Custom styling - Professional theme
st.markdown("""
    <style>
        /* Color scheme - Professional blues and greens */
        :root {
            --primary-color: #0066cc;
            --secondary-color: #00a86b;
            --accent-color: #ff6b6b;
            --bg-light: #f8f9fa;
            --bg-card: #ffffff;
            --text-dark: #1a1a1a;
            --text-light: #666666;
            --border-color: #e0e0e0;
        }
        
        /* Main container */
        .main {
            background-color: #f5f7fa;
        }
        
        /* Section headers - Uniform styling */
        .section-header {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 25px;
            margin-bottom: 20px;
            font-size: 18px;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Metric cards - Consistent layout */
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #0066cc;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 15px;
        }
        
        /* Info boxes */
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #0066cc;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        .warning-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        .success-box {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
        }
        
        /* Dataframe styling */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background-color: white;
            padding: 0px;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .stTabs [aria-selected="true"] {
            border-bottom: 3px solid #0066cc !important;
            color: #0066cc !important;
        }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_statistics():
    """Fetch statistics from MongoDB"""
    try:
        if MONGO_AVAILABLE and db:
            hs_codes_col = db["hs_codes"]
            total_codes = hs_codes_col.count_documents({})
            export_count = hs_codes_col.count_documents({"trade_type": "EXPORT"})
            import_count = hs_codes_col.count_documents({"trade_type": "IMPORT"})
            
            return {
                "total_hs_codes": total_codes,
                "export_codes": export_count,
                "import_codes": import_count,
                "data_date": "2026-01-21"
            }
        else:
            # Fallback if MongoDB unavailable
            return {
                "total_hs_codes": 13,
                "export_codes": 12,
                "import_codes": 1,
                "data_date": "2026-01-21"
            }
    except Exception as e:
        st.warning(f"Could not fetch live statistics: {str(e)}")
        return {"total_hs_codes": 13, "export_codes": 12, "import_codes": 1, "data_date": "2026-01-21"}


@st.cache_data(ttl=300)
def get_hs_codes(trade_mode=None, limit=100, skip=0):
    """Fetch HS codes from MongoDB"""
    try:
        if MONGO_AVAILABLE and db:
            hs_codes_col = db["hs_codes"]
            query = {}
            if trade_mode:
                query["trade_type"] = trade_mode.upper()
            
            codes = list(hs_codes_col.find(query).skip(skip).limit(limit))
            return [{"hs_code": c.get("hs_code"), "product_label": c.get("product_label"), "trade_type": c.get("trade_type")} for c in codes]
        else:
            return []
    except Exception as e:
        st.warning(f"Could not fetch HS codes: {str(e)}")
        return []


def get_hs_code_detail(hs_code, trade_mode=None):
    """Fetch detailed data for a specific HS code from MongoDB"""
    try:
        if MONGO_AVAILABLE and db:
            hs_codes_col = db["hs_codes"]
            query = {"hs_code": hs_code}
            if trade_mode:
                query["trade_type"] = trade_mode.upper()
            
            result = hs_codes_col.find_one(query)
            if result:
                result.pop("_id", None)  # Remove MongoDB ID
                return result
        return None
    except Exception as e:
        st.warning(f"Could not fetch HS code details: {str(e)}")
        return None


def search_hs_codes(hs_code=None, trade_mode=None, min_completeness=0):
    """Search HS codes with filters using MongoDB"""
    try:
        if MONGO_AVAILABLE and db:
            hs_codes_col = db["hs_codes"]
            query = {}
            
            if hs_code:
                query["hs_code"] = {"$regex": hs_code, "$options": "i"}
            if trade_mode:
                query["trade_type"] = trade_mode.upper()
            
            results = list(hs_codes_col.find(query).limit(200))
            return {
                "count": len(results),
                "data": [{"hs_code": r.get("hs_code"), "product_label": r.get("product_label"), "trade_type": r.get("trade_type")} for r in results]
            }
        else:
            return {"count": 0, "data": []}
    except Exception as e:
        st.warning(f"Search failed: {str(e)}")
        return {"count": 0, "data": []}


def compare_hs_codes(codes, trade_mode=None):
    """Compare multiple HS codes using MongoDB"""
    try:
        if MONGO_AVAILABLE and db:
            hs_codes_col = db["hs_codes"]
            query = {"hs_code": {"$in": codes}}
            
            if trade_mode:
                query["trade_type"] = trade_mode.upper()
            
            results = list(hs_codes_col.find(query))
            comparison_data = {}
            for r in results:
                comparison_data[r.get("hs_code")] = r
            
            return comparison_data
        else:
            return {}
    except Exception as e:
        st.warning(f"Comparison failed: {str(e)}")
        return {}


# ==================== HOME PAGE ====================

def page_home():
    """Home page with overview and KPIs"""
    st.markdown("# 📊 India Trade Statistics Dashboard")
    st.markdown("#### Real-time monitoring of India's Export & Import data by HS Code")
    st.markdown("**Reporting Country: 🇮🇳 India** | Data Updated: 2026-01-21")
    
    st.divider()
    
    # Fetch statistics
    stats = get_statistics()
    
    if stats:
        # Context Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">REPORTING ENTITY</div>
                <div style="font-size: 20px; font-weight: bold; color: #0066cc;">🇮🇳 India</div>
                <div style="font-size: 11px; color: #666; margin-top: 5px;">Ministry of Commerce & Industry</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            export_count = stats.get('export_records', 0)
            import_count = stats.get('import_records', 0)
            total = export_count + import_count
            export_pct = (export_count / max(total, 1)) * 100
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">TRADE DATA COMPOSITION</div>
                <div style="font-size: 18px; font-weight: bold; color: #00a86b;">Exports: {export_pct:.0f}%</div>
                <div style="font-size: 11px; color: #666; margin-top: 5px;">Imports: {100-export_pct:.0f}% | Total: {total:,} records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">MARKET COVERAGE</div>
                <div style="font-size: 18px; font-weight: bold; color: #ff6b6b;">{stats.get('unique_countries', 0)} Countries</div>
                <div style="font-size: 11px; color: #666; margin-top: 5px;>{stats.get('total_hs_codes', 0)} HS Codes | {len(stats.get('years_covered', []))} Years</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # KPI Metrics - Bifurcated by Trade Mode
        st.markdown("### 📈 India's Trade Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total HS Codes",
                value=stats.get("total_hs_codes", 0),
                delta="Tracked Commodities"
            )
        
        with col2:
            st.metric(
                label="Export Records",
                value=f"{export_count:,}",
                delta="Indian Exports"
            )
        
        with col3:
            st.metric(
                label="Import Records",
                value=f"{import_count:,}",
                delta="Indian Imports"
            )
        
        with col4:
            st.metric(
                label="Avg Completeness",
                value=f"{stats.get('avg_data_completeness', 0):.1f}%",
                delta="Data Quality"
            )
        
        st.divider()
        
        # Trade Mode Distribution
        st.markdown("### 🔄 Export vs Import Distribution")
        
        col1, col2, col3 = st.columns([1.5, 1, 1])
        
        with col1:
            trade_data = {
                'Trade Mode': ['🚀 EXPORTS (Made in India)', '📦 IMPORTS (Imported to India)'],
                'Records': [export_count, import_count],
                'Percentage': [export_pct, 100-export_pct]
            }
            trade_df = pd.DataFrame(trade_data)
            
            fig_trade = px.bar(
                trade_df,
                x='Trade Mode',
                y='Records',
                title='India Trade Data Volume',
                labels={'Records': 'Number of Records'},
                color='Trade Mode',
                color_discrete_map={
                    '🚀 EXPORTS (Made in India)': '#00CC96',
                    '📦 IMPORTS (Imported to India)': '#636EFA'
                },
                text='Records'
            )
            fig_trade.update_traces(textposition='outside')
            fig_trade.update_layout(template="plotly_white", height=400, showlegend=False)
            st.plotly_chart(fig_trade, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(
                trade_df,
                names='Trade Mode',
                values='Records',
                title="Trade Split",
                color_discrete_map={
                    '🚀 EXPORTS (Made in India)': '#00CC96',
                    '📦 IMPORTS (Imported to India)': '#636EFA'
                }
            )
            fig_pie.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col3:
            st.markdown("""
            <div class="success-box">
                <h4 style="margin-top: 0;">📊 Key Facts</h4>
                <ul style="margin: 10px 0; padding-left: 20px; font-size: 12px;">
                    <li>India's export records form the bulk of tracked data</li>
                    <li>Multi-product export portfolio</li>
                    <li>Diversified trading partners (200+ countries)</li>
                    <li>7 years of historical trend data available</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Data Completeness
        st.markdown("### 📋 Data Quality Assessment")
        
        completeness = stats['avg_data_completeness']
        col1, col2 = st.columns(2)
        
        with col1:
            fig_gauge = go.Figure(data=[
                go.Indicator(
                    mode="gauge+number+delta",
                    value=completeness,
                    title={'text': "Data Completeness %"},
                    delta={'reference': 80},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#0066cc"},
                        'steps': [
                            {'range': [0, 50], 'color': "#ffcccc"},
                            {'range': [50, 80], 'color': "#ffffcc"},
                            {'range': [80, 100], 'color': "#ccffcc"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                )
            ])
            fig_gauge.update_layout(height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4 style="margin-top: 0;">Quality Metrics</h4>
                <div style="margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Total Records:</span>
                        <span style="font-weight: bold; color: #0066cc;">{stats.get('total_records_captured', 0):,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span>Unique Countries:</span>
                        <span style="font-weight: bold; color: #00a86b;">{stats.get('unique_countries', 0)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Years Covered:</span>
                        <span style="font-weight: bold; color: #ffc107;">
                            {min(stats.get('years_covered', []))} to {max(stats.get('years_covered', []))}
                        </span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.caption(f"Last updated: {stats.get('last_scrape_time', 'N/A')} | Dashboard for India's Trade Ministry Data")
    
    else:
        st.warning("Unable to fetch statistics. Is the API running on localhost:8000?")


# ==================== HS CODE DETAILS PAGE ====================

def page_hs_code_details():
    """Detailed view for a specific HS code with comprehensive analysis"""
    st.markdown("# 🔍 India Trade Analysis - Commodity Level Intelligence")
    st.markdown("**Reporting Country: 🇮🇳 India** | Analyze India's Export & Import Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hs_code = st.text_input(
            "Enter HS Code",
            placeholder="e.g., 61091000",
            help="8-digit Harmonized System code"
        )
    
    with col2:
        trade_mode = st.selectbox(
            "Trade Mode",
            options=["Both", "Export", "Import"],
            help="Filter by India's trade direction"
        )
    
    with col3:
        analysis_type = st.selectbox(
            "Analysis Type",
            options=["Overview", "Country Drill-Down", "Growth Analysis"]
        )
    
    if hs_code:
        # Convert trade mode
        api_trade_mode = None if trade_mode == "Both" else trade_mode.lower()
        data = get_hs_code_detail(hs_code, api_trade_mode)
        
        if data:
            st.success(f"✅ Data found for HS Code: {hs_code}")
            
            metadata = data.get("metadata", {})
            years_data = data.get("data_by_year", {})
            
            if analysis_type == "Overview":
                page_hs_overview(hs_code, metadata, years_data, trade_mode)
            elif analysis_type == "Country Drill-Down":
                page_hs_country_drilldown(hs_code, metadata, years_data, trade_mode)
            elif analysis_type == "Growth Analysis":
                page_hs_growth_analysis(hs_code, metadata, years_data, trade_mode)
        
        else:
            st.warning(f"No data found for HS Code: {hs_code}")
    
    else:
        st.info("👉 Enter an HS Code to begin analysis")


# ==================== SEARCH & FILTER PAGE ====================

def page_search_filter():
    """Advanced search and filtering"""
    st.markdown("# 🔎 Search & Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hs_code_filter = st.text_input("HS Code (partial match)", placeholder="61091")
    
    with col2:
        trade_mode_filter = st.selectbox(
            "Trade Mode",
            options=[None, "export", "import"],
            format_func=lambda x: "All" if x is None else x.capitalize()
        )
    
    with col3:
        min_completeness = st.slider(
            "Min Data Completeness %",
            min_value=0,
            max_value=100,
            value=0,
            step=5
        )
    
    if st.button("🔍 Search", key="search_btn"):
        results = search_hs_codes(
            hs_code=hs_code_filter if hs_code_filter else None,
            trade_mode=trade_mode_filter,
            min_completeness=min_completeness
        )
        
        count = results.get("count", 0)
        st.info(f"Found **{count}** matching records")
        
        if count > 0:
            # Display results
            data = results.get("data", [])
            
            # Create DataFrame
            df_data = []
            for record in data:
                metadata = record.get("metadata", {})
                df_data.append({
                    "HS Code": record.get("hs_code"),
                    "Trade Mode": record.get("trade_mode").capitalize(),
                    "Product": metadata.get("product_label", ""),
                    "Completeness %": metadata.get("data_completeness_percent", 0),
                    "Countries": metadata.get("unique_partner_countries", 0),
                    "Records": metadata.get("total_records_captured", 0)
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


# ==================== COMPARISON PAGE ====================

def page_comparison():
    """Compare multiple HS codes"""
    st.markdown("# ⚖️ HS Code Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        codes_input = st.text_input(
            "Enter HS Codes (comma-separated)",
            placeholder="61091000,03061710,84135010",
            help="Enter multiple HS codes separated by commas"
        )
    
    with col2:
        trade_mode = st.selectbox(
            "Trade Mode",
            options=[None, "export", "import"],
            format_func=lambda x: "All" if x is None else x.capitalize(),
            key="compare_mode"
        )
    
    if st.button("⚖️ Compare", key="compare_btn"):
        if codes_input:
            codes = [c.strip() for c in codes_input.split(",")]
            comparison = compare_hs_codes(codes, trade_mode)
            
            if comparison:
                st.success(f"Comparing {len(comparison)} HS codes")
                
                # Create comparison table
                comparison_data = []
                for code, data in comparison.items():
                    comparison_data.append({
                        "HS Code": code,
                        "Trade Mode": data["trade_mode"].capitalize(),
                        "Completeness %": data["completeness"],
                        "Partner Countries": data["countries"],
                        "Years": len(data.get("years", []))
                    })
                
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True)
                
                # Completeness comparison chart
                fig = px.bar(
                    df,
                    x="HS Code",
                    y="Completeness %",
                    color="Trade Mode",
                    title="Data Completeness Comparison",
                    barmode="group"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Partners comparison
                fig = px.bar(
                    df,
                    x="HS Code",
                    y="Partner Countries",
                    color="Trade Mode",
                    title="Partner Countries Comparison",
                    barmode="group"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No comparison data available")
        else:
            st.warning("Please enter at least one HS code")


# ==================== ANALYTICS PAGE ====================

def page_analytics():
    """Analytics and insights"""
    st.markdown("# � Market Analytics & Business Intelligence")
    
    st.markdown("### 💡 Dataset Overview")
    
    stats = get_statistics()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_hs_codes = stats.get("total_hs_codes", 0)
            st.metric("Total HS Codes Analyzed", f"{total_hs_codes:,}")
        
        with col2:
            countries = stats.get("unique_countries", 0)
            st.metric("Partner Countries", f"{countries:,}")
        
        with col3:
            years = stats.get("years_covered", [])
            st.metric("Historical Data", f"{len(years)} years")
        
        with col4:
            export_pct = (stats.get("export_records", 0) / max(stats.get("total_records_captured", 1), 1)) * 100
            st.metric("Export Share", f"{export_pct:.1f}%")
        
        st.divider()
        
        # Export vs Import analysis
        st.markdown("### 🔄 Trade Mode Analysis")
        
        col1, col2 = st.columns([1.2, 0.8])
        
        with col1:
            # Trade mode distribution with values
            trade_data = {
                'Mode': ['Export', 'Import'],
                'Records': [stats.get('export_records', 0), stats.get('import_records', 0)]
            }
            trade_df = pd.DataFrame(trade_data)
            
            fig_trade = px.bar(
                trade_df,
                x='Mode',
                y='Records',
                title='Export vs Import Records',
                labels={'Records': 'Number of Records'},
                color='Mode',
                color_discrete_map={'Export': '#00CC96', 'Import': '#636EFA'}
            )
            st.plotly_chart(fig_trade, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(
                trade_df,
                names='Mode',
                values='Records',
                title="Trade Mode Split",
                color_discrete_map={'Export': '#00CC96', 'Import': '#636EFA'}
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        
        # Business recommendations
        st.markdown("### 📌 Business Insights & Recommendations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **📈 Market Opportunities:**
            - 12 HS codes with complete data
            - Up to 214 partner countries per commodity
            - 7 years of historical trends
            """)
        
        with col2:
            st.success("""
            **💰 Business Use Cases:**
            - Market penetration analysis
            - Competitor benchmarking
            - Export potential assessment
            - Import substitution opportunities
            """)
        
        with col3:
            st.warning("""
            **⚠️ Key Metrics to Monitor:**
            - Market concentration risk
            - Year-over-year growth rates
            - Geographic diversification
            - Product competitiveness
            """)
            # Mode ratio
            export_ratio = stats['export_records'] / (stats['export_records'] + stats['import_records'] + 1) * 100
            import_ratio = 100 - export_ratio
            
            st.info(f"**Export**: {export_ratio:.1f}%")
            st.info(f"**Import**: {import_ratio:.1f}%")
        
        # Completeness distribution
        st.markdown("### Data Completeness Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Average**: {stats['avg_data_completeness']:.1f}%")
        
        with col2:
            if stats['avg_data_completeness'] >= 80:
                st.success("✅ High quality data")
            elif stats['avg_data_completeness'] >= 60:
                st.warning("⚠️ Moderate quality data")
            else:
                st.error("❌ Low quality data")


# ==================== HS CODE OVERVIEW FUNCTION ====================

def page_hs_overview(hs_code, metadata, years_data, trade_mode):
    """Comprehensive overview of HS code performance"""
    
    # Business KPIs
    st.markdown('<div class="section-header">💼 India\'s Commodity Profile & Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    trade_mode_label = "🚀 EXPORTS" if trade_mode == "Export" else "📦 IMPORTS" if trade_mode == "Import" else "🔄 BOTH"
    
    with col1:
        product = metadata.get("product_label", "N/A")
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">Product Category</div>
            <div style="font-size: 14px; font-weight: bold; color: #0066cc; margin-top: 8px;">
                {product[:30] if product != "N/A" else "N/A"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        partners = metadata.get("unique_partner_countries", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">Trading Partners</div>
            <div style="font-size: 14px; font-weight: bold; color: #00a86b; margin-top: 8px;">
                {partners} Countries
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        years = metadata.get("number_of_years", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">Data Span</div>
            <div style="font-size: 14px; font-weight: bold; color: #ff6b6b; margin-top: 8px;">
                {years} Years
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">Trade Direction</div>
            <div style="font-size: 14px; font-weight: bold; color: #ffc107; margin-top: 8px;">
                {trade_mode_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if not years_data:
        st.warning("No detailed data available for this HS code")
        return
    
    st.divider()
    
    # Performance Summary
    st.markdown('<div class="section-header">📊 India\'s Trade Performance - 7-Year Summary</div>', unsafe_allow_html=True)
    
    latest_year = sorted(years_data.keys())[-1]
    oldest_year = sorted(years_data.keys())[0]
    prev_year = sorted(years_data.keys())[-2] if len(years_data) >= 2 else oldest_year
    
    latest_data = years_data[latest_year]
    prev_data = years_data[prev_year]
    
    latest_partners = latest_data.get("partner_countries", [])
    latest_total = sum([float(p.get(latest_year) or 0) for p in latest_partners])
    
    prev_partners = prev_data.get("partner_countries", [])
    prev_total = sum([float(p.get(prev_year) or 0) for p in prev_partners])
    
    oldest_partners = years_data[oldest_year].get("partner_countries", [])
    oldest_total = sum([float(p.get(oldest_year) or 0) for p in oldest_partners])
    
    yoy_growth = ((latest_total - prev_total) / max(prev_total, 0.01)) * 100 if prev_total > 0 else 0
    growth_pct = ((latest_total - oldest_total) / max(oldest_total, 0.01)) * 100 if oldest_total > 0 else 0
    
    years_count = len(years_data) - 1
    if years_count > 0 and oldest_total > 0:
        cagr = (((latest_total / oldest_total) ** (1/years_count)) - 1) * 100
    else:
        cagr = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        growth_indicator = "📈" if yoy_growth >= 0 else "📉"
        color = "#00a86b" if yoy_growth >= 0 else "#ff6b6b"
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">{latest_year} Value</div>
            <div style="font-size: 16px; font-weight: bold; color: #0066cc; margin-top: 8px;">
                ${latest_total:,.1f}M
            </div>
            <div style="font-size: 11px; color: {color}; margin-top: 8px;">
                {growth_indicator} YoY: {yoy_growth:+.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">Active Partners</div>
            <div style="font-size: 16px; font-weight: bold; color: #00a86b; margin-top: 8px;">
                {len(latest_partners)}
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 8px;">
                Countries
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cagr_color = "#00a86b" if cagr >= 0 else "#ff6b6b"
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">CAGR (7-Yr)</div>
            <div style="font-size: 16px; font-weight: bold; color: {cagr_color}; margin-top: 8px;">
                {cagr:+.1f}%
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 8px;">
                Growth Rate
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_growth_color = "#00a86b" if growth_pct >= 0 else "#ff6b6b"
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 11px; color: #666;">7-Year Growth</div>
            <div style="font-size: 16px; font-weight: bold; color: {total_growth_color}; margin-top: 8px;">
                {growth_pct:+.1f}%
            </div>
            <div style="font-size: 11px; color: #666; margin-top: 8px;">
                {oldest_year} to {latest_year}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Multi-chart analysis
    st.markdown('<div class="section-header">📈 India\'s Trade Trends & Market Dynamics</div>', unsafe_allow_html=True)
    
    # Prepare trend data
    trend_data = []
    for year in sorted(years_data.keys()):
        year_detail = years_data[year]
        partners = year_detail.get("partner_countries", [])
        total_value = sum([float(p.get(year) or 0) for p in partners])
        trend_data.append({"Year": year, "Trade Value (USD M)": total_value, "Partner Count": len(partners)})
    
    trend_df = pd.DataFrame(trend_data)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Value Trends", "🌍 Partners Trend", "📈 Growth Rate"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            fig_trend = px.line(
                trend_df,
                x="Year",
                y="Trade Value (USD M)",
                markers=True,
                title=f"India's {trade_mode_label} Value - {hs_code}",
                line_shape="spline"
            )
            fig_trend.update_traces(line=dict(color="#0066cc", width=3), marker=dict(size=10))
            fig_trend.update_layout(template="plotly_white", hovermode="x unified", height=450)
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            if len(trend_data) >= 2:
                metrics_summary = f"""
                **Summary Metrics**
                
                - Latest: ${trend_data[-1]['Trade Value (USD M)']:,.1f}M
                - Avg: ${sum([t['Trade Value (USD M)'] for t in trend_data])/len(trend_data):,.1f}M  
                - Max: ${max([t['Trade Value (USD M)'] for t in trend_data]):,.1f}M
                - Min: ${min([t['Trade Value (USD M)'] for t in trend_data]):,.1f}M
                """
                st.markdown(metrics_summary)
    
    with tab2:
        fig_partners = px.area(
            trend_df,
            x="Year",
            y="Partner Count",
            title="India's Trading Partner Expansion"
        )
        fig_partners.update_layout(template="plotly_white", height=400, hovermode="x unified")
        st.plotly_chart(fig_partners, use_container_width=True)
    
    with tab3:
        trend_df["Growth %"] = trend_df["Trade Value (USD M)"].pct_change() * 100
        
        fig_growth = px.bar(
            trend_df.dropna(),
            x="Year",
            y="Growth %",
            color="Growth %",
            color_continuous_scale=["#ff6b6b", "#ffc107", "#00a86b"],
            title="Year-on-Year Growth Rate",
            text="Growth %"
        )
        fig_growth.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_growth.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig_growth, use_container_width=True)
    
    st.divider()
    
    # Top 15 Partners
    st.markdown('<div class="section-header">🏆 India\'s Top Trading Partners</div>', unsafe_allow_html=True)
    
    all_partners = latest_data.get("partner_countries", [])
    
    country_values = []
    for partner in all_partners:
        country = partner.get("Country") or partner.get("country", "Unknown")
        value = float(partner.get(latest_year) or 0)
        if value > 0:
            country_values.append({"Country": country, "Value": value})
    
    country_values_sorted = sorted(country_values, key=lambda x: x["Value"], reverse=True)[:15]
    
    if country_values_sorted:
        top_countries_df = pd.DataFrame(country_values_sorted)
        total_all = sum([c["Value"] for c in country_values_sorted])
        top_countries_df["Share %"] = (top_countries_df["Value"] / total_all * 100).round(2)
        top_countries_df["Rank"] = range(1, len(top_countries_df) + 1)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_bar = px.bar(
                top_countries_df,
                y="Country",
                x="Value",
                orientation="h",
                title=f"Top 15 Partners - {latest_year}",
                color="Value",
                color_continuous_scale="Blues",
                text="Share %"
            )
            fig_bar.update_traces(texttemplate="<b>%{text:.1f}%</b>", textposition="inside")
            fig_bar.update_xaxes(autorange="reversed")
            fig_bar.update_layout(template="plotly_white", height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(
                top_countries_df,
                names="Country",
                values="Value",
                title="Market Share Distribution"
            )
            fig_pie.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_pie, use_container_width=True)


# ==================== COUNTRY DRILL-DOWN FUNCTION ====================

def page_hs_country_drilldown(hs_code, metadata, years_data, trade_mode):
    """Drill-down analysis by country"""
    
    st.markdown('<div class="section-header">🌐 Country-Level Analysis & Performance</div>', unsafe_allow_html=True)
    st.markdown("Select a country to analyze its trading relationship with India for this commodity")
    
    if not years_data:
        st.warning("No data available")
        return
    
    latest_year = sorted(years_data.keys())[-1]
    latest_data = years_data[latest_year]
    all_partners = latest_data.get("partner_countries", [])
    
    # Get list of countries
    countries_list = sorted(set([p.get("Country") or p.get("country", "Unknown") for p in all_partners]))
    
    selected_country = st.selectbox(
        "Select Country to Analyze",
        options=countries_list,
        help="Choose a country to see detailed trade metrics"
    )
    
    if selected_country:
        st.divider()
        st.markdown(f'<div class="section-header">📊 {selected_country.upper()} - Trade Profile for HS Code {hs_code}</div>', unsafe_allow_html=True)
        
        # Extract country data across all years
        country_timeline = []
        for year in sorted(years_data.keys()):
            year_data = years_data[year]
            partners = year_data.get("partner_countries", [])
            
            for partner in partners:
                country_name = partner.get("Country") or partner.get("country", "Unknown")
                if country_name == selected_country:
                    value = float(partner.get(year) or 0)
                    country_timeline.append({
                        "Year": year,
                        "Value": value,
                        "Product": year_data.get("product_label", "")
                    })
                    break
        
        if country_timeline:
            country_df = pd.DataFrame(country_timeline)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            latest_value = country_df.iloc[-1]["Value"]
            oldest_value = country_df.iloc[0]["Value"]
            avg_value = country_df["Value"].mean()
            
            country_growth = ((latest_value - oldest_value) / max(oldest_value, 0.01)) * 100 if oldest_value > 0 else 0
            growth_indicator = "📈" if country_growth >= 0 else "📉"
            color = "#00a86b" if country_growth >= 0 else "#ff6b6b"
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 11px; color: #666;">Current Value ({latest_year})</div>
                    <div style="font-size: 16px; font-weight: bold; color: #0066cc; margin-top: 8px;">
                        ${latest_value:,.1f}M
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 11px; color: #666;">Average Value</div>
                    <div style="font-size: 16px; font-weight: bold; color: #00a86b; margin-top: 8px;">
                        ${avg_value:,.1f}M
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 11px; color: #666;">7-Year Growth</div>
                    <div style="font-size: 16px; font-weight: bold; color: {color}; margin-top: 8px;">
                        {growth_indicator} {country_growth:+.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                trend = "↗️ Growing" if country_growth > 0 else "↘️ Declining" if country_growth < 0 else "→ Stable"
                trend_color = "#00a86b" if country_growth > 0 else "#ff6b6b" if country_growth < 0 else "#ffc107"
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 11px; color: #666;">Trend</div>
                    <div style="font-size: 16px; font-weight: bold; color: {trend_color}; margin-top: 8px;">
                        {trend}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig_country = px.line(
                    country_df,
                    x="Year",
                    y="Value",
                    markers=True,
                    title=f"India to {selected_country} Trade Value",
                    line_shape="spline"
                )
                fig_country.update_traces(line=dict(color="#0066cc", width=3), marker=dict(size=10))
                fig_country.update_layout(template="plotly_white", hovermode="x unified", height=400)
                st.plotly_chart(fig_country, use_container_width=True)
            
            with col2:
                country_df["Growth %"] = country_df["Value"].pct_change() * 100
                
                fig_growth = px.bar(
                    country_df.dropna(),
                    x="Year",
                    y="Growth %",
                    color="Growth %",
                    color_continuous_scale=["#ff6b6b", "#ffffcc", "#00a86b"],
                    title=f"{selected_country} - YoY Growth"
                )
                fig_growth.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig_growth, use_container_width=True)
            
            # Table
            st.markdown("**Detailed Timeline**")
            display_df = country_df.copy()
            display_df["Value"] = display_df["Value"].apply(lambda x: f"${x:,.1f}M")
            display_df = display_df[["Year", "Value"]]
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        else:
            st.warning(f"No trade data found for {selected_country}")


# ==================== GROWTH ANALYSIS FUNCTION ====================

def page_hs_growth_analysis(hs_code, metadata, years_data, trade_mode):
    """Deep growth analysis"""
    
    st.markdown('<div class="section-header">📈 Growth Dynamics & Market Analysis</div>', unsafe_allow_html=True)
    
    if not years_data:
        st.warning("No data available")
        return
    
    # Prepare comprehensive data
    trend_data = []
    for year in sorted(years_data.keys()):
        year_detail = years_data[year]
        partners = year_detail.get("partner_countries", [])
        
        total_value = 0
        top_3_value = 0
        
        country_values = []
        for partner in partners:
            value = float(partner.get(year) or 0)
            total_value += value
            country_values.append({"Country": partner.get("Country") or partner.get("country"), "Value": value})
        
        # Top 3
        sorted_countries = sorted(country_values, key=lambda x: x["Value"], reverse=True)
        top_3_value = sum([c["Value"] for c in sorted_countries[:3]])
        
        concentration = (top_3_value / total_value * 100) if total_value > 0 else 0
        
        trend_data.append({
            "Year": year,
            "Total Value": total_value,
            "Partner Count": len(partners),
            "Top 3 Concentration %": concentration
        })
    
    trend_df = pd.DataFrame(trend_data)
    
    # Multi-chart view
    col1, col2 = st.columns(2)
    
    with col1:
        # Value and concentration
        fig = px.line(
            trend_df,
            x="Year",
            y="Total Value",
            title="Total Trade Value Growth",
            markers=True,
            line_shape="spline"
        )
        fig.update_traces(line=dict(color="#0066cc", width=3), marker=dict(size=10))
        fig.update_layout(template="plotly_white", hovermode="x unified", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(
            trend_df,
            x="Year",
            y="Top 3 Concentration %",
            title="Market Concentration Risk",
            markers=True,
            line_shape="spline"
        )
        fig.update_traces(line=dict(color="#ff6b6b", width=3), marker=dict(size=10))
        fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
        fig.update_layout(template="plotly_white", hovermode="x unified", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Partner expansion
    st.markdown("### Market Expansion - New Partners Added")
    
    fig = px.area(
        trend_df,
        x="Year",
        y="Partner Count",
        title="India's Trading Partners Growth"
    )
    fig.update_layout(template="plotly_white", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.markdown("### Growth Summary")
    display_trend = trend_df.copy()
    display_trend["Total Value"] = display_trend["Total Value"].apply(lambda x: f"${x:,.1f}M")
    display_trend["Top 3 Concentration %"] = display_trend["Top 3 Concentration %"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(display_trend, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # World Map - Geographic Distribution
    st.markdown('<div class="section-header">🌍 Geographic Trade Distribution</div>', unsafe_allow_html=True)
    
    if years_data:
        latest_year = sorted(years_data.keys())[-1]
        latest_data = years_data[latest_year]
        all_partners = latest_data.get("partner_countries", [])
        
        if all_partners:
            # Country coordinates mapping
            country_coords = {
                'UNITED STATES': (37.0902, -95.7129),
                'CHINA': (35.8617, 104.1954),
                'JAPAN': (36.2048, 138.2529),
                'GERMANY': (51.1657, 10.4515),
                'UNITED KINGDOM': (55.3781, -3.4360),
                'FRANCE': (46.2276, 2.2137),
                'INDIA': (20.5937, 78.9629),
                'SOUTH KOREA': (35.9078, 127.7669),
                'ITALY': (41.8719, 12.5674),
                'SPAIN': (40.4637, -3.7492),
                'CANADA': (56.1304, -106.3468),
                'MEXICO': (23.6345, -102.5528),
                'BRAZIL': (-14.2350, -51.9253),
                'AUSTRALIA': (-25.2744, 133.7751),
                'SINGAPORE': (1.3521, 103.8198),
                'HONG KONG': (22.3193, 114.1694),
                'UAE': (23.4241, 53.8478),
                'SAUDI ARABIA': (23.8859, 45.0792),
                'TURKEY': (38.9637, 35.2433),
                'THAILAND': (15.8700, 100.9925),
                'MALAYSIA': (4.2105, 101.6964),
                'INDONESIA': (-0.7893, 113.9213),
                'PHILIPPINES': (12.8797, 121.7740),
                'VIETNAM': (14.0583, 108.2772),
                'RUSSIA': (61.5240, 105.3188),
                'POLAND': (51.9194, 19.1451),
                'NETHERLANDS': (52.1326, 5.2913),
                'BELGIUM': (50.5039, 4.4699),
                'SWITZERLAND': (46.8182, 8.2275),
                'SWEDEN': (60.1282, 18.6435),
                'EGYPT': (26.8206, 30.8025),
                'ARGENTINA': (-38.4161, -63.6167),
                'NEW ZEALAND': (-40.9006, 174.8860),
            }
            
            # Prepare scatter data
            scatter_data = []
            for partner in all_partners:
                country = (partner.get("Country") or partner.get("country", "")).upper()
                value = float(partner.get(latest_year) or 0)
                
                coords = country_coords.get(country)
                if coords and value > 0:
                    scatter_data.append({
                        "Country": country,
                        "Lat": coords[0],
                        "Lon": coords[1],
                        "Value": value
                    })
            
            if scatter_data:
                scatter_df = pd.DataFrame(scatter_data)
                
                # Create scatter geo map
                fig_geo = px.scatter_geo(
                    scatter_df,
                    lat="Lat",
                    lon="Lon",
                    size="Value",
                    hover_name="Country",
                    hover_data={"Value": ":.2f", "Lat": False, "Lon": False},
                    title=f"Global Trade Partners - {hs_code} ({latest_year})",
                    size_max=50,
                    color="Value",
                    color_continuous_scale="Viridis",
                    projection="natural earth"
                )
                fig_geo.update_layout(
                    height=600,
                    showlegend=True,
                    geo=dict(
                        showland=True,
                        landcolor="rgb(243, 243, 243)",
                        showocean=True,
                        oceancolor="rgb(204, 229, 255)"
                    )
                )
                st.plotly_chart(fig_geo, use_container_width=True)
    
    st.divider()
    
    # Strategic Recommendations
    st.markdown('<div class="section-header">💡 Strategic Export Recommendations</div>', unsafe_allow_html=True)
    
    if years_data and len(years_data) >= 2:
        latest_year = sorted(years_data.keys())[-1]
        oldest_year = sorted(years_data.keys())[0]
        
        latest_data = years_data[latest_year]
        oldest_data = years_data[oldest_year]
        
        latest_partners = latest_data.get("partner_countries", [])
        oldest_partners = oldest_data.get("partner_countries", [])
        
        # Get existing countries
        existing_countries = set([(p.get("Country") or p.get("country", "")).upper() for p in latest_partners])
        initial_countries = set([(p.get("Country") or p.get("country", "")).upper() for p in oldest_partners])
        
        # Calculate growth
        latest_total = sum([float(p.get(latest_year) or 0) for p in latest_partners])
        oldest_total = sum([float(p.get(oldest_year) or 0) for p in oldest_partners])
        total_growth = ((latest_total - oldest_total) / max(oldest_total, 0.01)) * 100 if oldest_total > 0 else 0
        
        # New markets entered
        new_markets = existing_countries - initial_countries
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="success-box">
                <h4 style="margin-top: 0; color: #28a745;">✅ Current Market Position</h4>
                <p style="font-size: 13px; margin: 10px 0;">
                    <strong>Active in {len(latest_partners)} Countries</strong><br><br>
                    <strong>Growth:</strong> {total_growth:+.1f}%<br>
                    <strong>Trade Value:</strong> ${latest_total:,.1f}M
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if new_markets:
                st.markdown(f"""
                <div class="info-box">
                    <h4 style="margin-top: 0; color: #0066cc;">🚀 Recent Expansion</h4>
                    <p style="font-size: 13px; margin: 10px 0;">
                        <strong>New Markets Entered: {len(new_markets)}</strong><br><br>
                        <strong>Action:</strong><br>
                        • Consolidate presence in new markets<br>
                        • Build long-term partnerships<br>
                        • Increase shipment frequency
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                    <h4 style="margin-top: 0; color: #ff9800;">⚠️ Limited Expansion</h4>
                    <p style="font-size: 13px; margin: 10px 0;">
                        <strong>No new markets in recent years</strong><br><br>
                        <strong>Action:</strong><br>
                        • Research untapped regional markets<br>
                        • Target emerging economies<br>
                        • Explore FTA opportunities
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            # Find top growth opportunity
            country_growth = []
            if len(years_data) >= 2:
                prev_year = sorted(years_data.keys())[-2]
                for partner in latest_partners:
                    country = partner.get("Country") or partner.get("country", "Unknown")
                    current = float(partner.get(latest_year) or 0)
                    previous = float(partner.get(prev_year) or 0)
                    if previous > 0:
                        growth = ((current - previous) / previous) * 100
                        if current > 0:
                            country_growth.append({"Country": country, "Growth": growth, "Value": current})
                
                if country_growth:
                    top_growth = sorted(country_growth, key=lambda x: x["Growth"], reverse=True)[0]
                    st.markdown(f"""
                    <div class="success-box">
                        <h4 style="margin-top: 0; color: #28a745;">📈 Top Performer</h4>
                        <p style="font-size: 13px; margin: 10px 0;">
                            <strong>{top_growth['Country']}</strong><br><br>
                            <strong>YoY Growth:</strong> {top_growth['Growth']:+.1f}%<br>
                            <strong>Current Trade:</strong> ${top_growth['Value']:,.1f}M<br><br>
                            💡 <em>Fastest growing market - maintain momentum!</em>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)


# ==================== SETTINGS PAGE ====================

def page_settings():
    """Settings and configuration"""
    st.markdown("# ⚙️ Settings & Configuration")
    
    st.markdown("### API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**API Base URL**: {API_BASE_URL}")
    
    with col2:
        if st.button("🔄 Check API Health"):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ API is healthy and responding")
                    health_data = response.json()
                    st.json(health_data)
                else:
                    st.error(f"❌ API returned status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Failed to connect to API: {str(e)}")
    
    st.divider()
    
    st.markdown("### Dashboard Information")
    st.info("""
    **Trade Statistics Dashboard** is a real-time analytics platform for India's trade data.
    
    - **Data Source**: Daily web scraping from Indian trade ministry
    - **Update Frequency**: Configurable (default: daily at 2:00 AM)
    - **HS Codes**: 10,000+ tracked
    - **Trade Modes**: Export and Import
    - **Backend**: FastAPI + MongoDB
    """)
    
    st.divider()
    
    st.markdown("### Cache Information")
    st.warning("""
    Data cache is set to **5 minutes**. This means:
    - Statistics are refreshed every 5 minutes
    - Search results are cached for 5 minutes
    - Use the sidebar to force refresh if needed
    """)


# ==================== MAIN APP ====================

def main():
    """Main app"""
    
    # Sidebar navigation
    st.sidebar.title("📊 Trade Statistics")
    
    page = st.sidebar.radio(
        "Select Page",
        options=[
            "Home",
            "HS Code Details",
            "Search & Filter",
            "Comparison",
            "Analytics",
            "Settings"
        ],
        index=0
    )
    
    st.sidebar.divider()
    
    # Sidebar info
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    **Trade Statistics Dashboard**
    
    Real-time monitoring of India's trade data.
    
    - FastAPI Backend
    - MongoDB Database
    - Streamlit Frontend
    """)
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", key="refresh"):
        st.cache_data.clear()
        st.rerun()
    
    # Route pages
    if page == "Home":
        page_home()
    elif page == "HS Code Details":
        page_hs_code_details()
    elif page == "Search & Filter":
        page_search_filter()
    elif page == "Comparison":
        page_comparison()
    elif page == "Analytics":
        page_analytics()
    elif page == "Settings":
        page_settings()


if __name__ == "__main__":
    main()
