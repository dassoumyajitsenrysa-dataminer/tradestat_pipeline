"""
Real-time monitoring dashboard for the scraping pipeline.

Install: pip install streamlit plotly

Run: streamlit run monitor_dashboard.py
"""

import streamlit as st
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import json
import time

st.set_page_config(page_title="Trade Scraper Monitor", layout="wide")

DB_PATH = Path("data/hs_codes.db")
RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")


def get_db_connection():
    """Create a fresh connection each time (no caching)"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    return conn


def get_stats():
    """Get overall statistics from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM hs_codes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE export_status = 'completed'")
    export_completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE import_status = 'completed'")
    import_completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE error_count > 0")
    failed = cursor.fetchone()[0]
    
    conn.close()  # Close connection after use
    
    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "export_completed": export_completed,
        "import_completed": import_completed,
        "failed": failed
    }


def get_file_stats():
    """Get statistics about saved files"""
    stats = {
        "raw_export": len(list(RAW_DATA_DIR.glob("export/**/*.json"))),
        "raw_import": len(list(RAW_DATA_DIR.glob("import/**/*.json"))),
        "processed_export": len(list(PROCESSED_DATA_DIR.glob("export/**/*.json"))),
        "processed_import": len(list(PROCESSED_DATA_DIR.glob("import/**/*.json"))),
    }
    return stats


def get_recent_activity():
    """Get recently processed HS codes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT hs_code, export_status, import_status, error_count, last_error
        FROM hs_codes
        WHERE export_scraped_at IS NOT NULL OR import_scraped_at IS NOT NULL
        ORDER BY export_scraped_at DESC, import_scraped_at DESC
        LIMIT 20
    """)
    
    results = cursor.fetchall()
    conn.close()
    return results


def get_error_report():
    """Get failed HS codes with errors"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT hs_code, error_count, last_error, status
        FROM hs_codes
        WHERE error_count > 0
        ORDER BY error_count DESC
        LIMIT 50
    """)
    
    results = cursor.fetchall()
    conn.close()
    return results


# Title and refresh
st.title("🔍 Trade Scraper Pipeline Monitor")
st.markdown("Real-time monitoring dashboard for HS code scraping pipeline")

# Auto-refresh every 5 seconds
col1, col2, col3 = st.columns([8, 2, 2])
with col2:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

with col3:
    auto_refresh = st.checkbox("Auto-refresh", value=True)

if auto_refresh:
    time.sleep(5)  # Wait 5 seconds then rerun
    st.rerun()

# Get current stats (fresh from database)
stats = get_stats()
file_stats = get_file_stats()

# Display last updated time
st.caption(f"⏱️ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# KPI Metrics
st.subheader("📊 Key Performance Indicators")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total HS Codes", stats["total"])

with col2:
    completion_rate = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    st.metric("Completion Rate", f"{completion_rate:.1f}%", f"{stats['completed']} done")

with col3:
    st.metric("Pending", stats["pending"], "remaining")

with col4:
    st.metric("Failed", stats["failed"], delta_color="inverse")

with col5:
    estimated_hours = (stats["pending"] * 75 / 60 / 4) if stats["pending"] > 0 else 0
    st.metric("Est. Time", f"{estimated_hours:.0f}h", f"@ 4 workers")

# Progress Charts
st.subheader("📈 Progress Overview")
col1, col2 = st.columns(2)

with col1:
    # Status distribution pie chart
    status_data = {
        "Completed": stats["completed"],
        "Pending": stats["pending"],
        "Failed": stats["failed"]
    }
    fig = go.Figure(data=[go.Pie(
        labels=list(status_data.keys()),
        values=list(status_data.values()),
        hole=0.3,
        marker=dict(colors=['#2ecc71', '#3498db', '#e74c3c'])
    )])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Export vs Import status
    import_export = {
        "Export Done": stats["export_completed"],
        "Import Done": stats["import_completed"],
        "Pending": stats["pending"]
    }
    fig = go.Figure(data=[go.Bar(
        x=list(import_export.keys()),
        y=list(import_export.values()),
        marker=dict(color=['#f39c12', '#9b59b6', '#95a5a6'])
    )])
    fig.update_layout(height=300, xaxis_title="Status", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

# File Storage Stats
st.subheader("💾 Data Storage")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Raw Export Files", file_stats["raw_export"])

with col2:
    st.metric("Raw Import Files", file_stats["raw_import"])

with col3:
    st.metric("Processed Export", file_stats["processed_export"])

with col4:
    st.metric("Processed Import", file_stats["processed_import"])

# Recent Activity
st.subheader("🔄 Recent Activity (Last 20)")
recent = get_recent_activity()

if recent:
    activity_data = []
    for hs_code, exp_status, imp_status, error_count, last_error in recent:
        activity_data.append({
            "HS Code": hs_code,
            "Export": exp_status,
            "Import": imp_status,
            "Errors": error_count,
            "Last Error": last_error[:50] if last_error else "None"
        })
    
    st.dataframe(activity_data, use_container_width=True, height=300)
else:
    st.info("No recent activity yet")

# Error Report
if stats["failed"] > 0:
    st.subheader("⚠️ Error Report")
    errors = get_error_report()
    
    error_data = []
    for hs_code, error_count, last_error, status in errors:
        error_data.append({
            "HS Code": hs_code,
            "Error Count": error_count,
            "Status": status,
            "Last Error": (last_error[:80] if last_error else "No error message")
        })
    
    st.dataframe(error_data, use_container_width=True, height=300)

# System Info
st.subheader("ℹ️ System Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Database Location:** `{DB_PATH}`")

with col2:
    st.info(f"**Raw Data:** `{RAW_DATA_DIR}`")

with col3:
    st.info(f"**Processed Data:** `{PROCESSED_DATA_DIR}`")

# Footer
st.markdown("---")
st.markdown(
    f"Last updated: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}** | "
    f"Auto-refresh every 30 seconds"
)
