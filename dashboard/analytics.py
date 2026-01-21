"""
Custom metrics and analysis functions for Trade Data Dashboard
Generates insights and metrics from trade datasets
"""

import pandas as pd
import numpy as np
from datetime import datetime


def calculate_growth_metrics(values, years):
    """Calculate growth metrics"""
    if len(values) < 2:
        return {"yoy_growth": 0, "cagr": 0, "trend": "stable"}
    
    # Year-over-year growth
    yoy_growth = ((values[-1] - values[-2]) / abs(values[-2]) * 100) if values[-2] != 0 else 0
    
    # CAGR (Compound Annual Growth Rate)
    if values[0] > 0 and values[-1] > 0:
        cagr = (((values[-1] / values[0]) ** (1 / (len(values) - 1))) - 1) * 100
    else:
        cagr = 0
    
    # Trend
    if yoy_growth > 10:
        trend = "Strong Growth"
    elif yoy_growth > 0:
        trend = "Positive"
    elif yoy_growth > -10:
        trend = "Slight Decline"
    else:
        trend = "Declining"
    
    return {
        "yoy_growth": yoy_growth,
        "cagr": cagr,
        "trend": trend
    }


def calculate_concentration(values):
    """Calculate market concentration (Herfindahl index)"""
    total = sum(values) if sum(values) > 0 else 1
    shares = [v / total for v in values]
    herfindahl = sum(s ** 2 for s in shares)
    
    # Normalize to 0-100
    normalized = (herfindahl - 1/len(values)) / (1 - 1/len(values)) * 100 if len(values) > 1 else 100
    
    if normalized > 70:
        concentration = "High (Monopolistic)"
    elif normalized > 40:
        concentration = "Moderate"
    else:
        concentration = "Low (Diversified)"
    
    return {
        "herfindahl": herfindahl,
        "normalized_concentration": normalized,
        "concentration_level": concentration
    }


def get_top_countries(partners_data, limit=10):
    """Get top trading partners"""
    if not partners_data:
        return []
    
    # Sort by latest year value
    sorted_partners = sorted(
        partners_data,
        key=lambda x: float(x.get("2024-2025", x.get("2023-2024", 0)) or 0),
        reverse=True
    )
    
    return sorted_partners[:limit]


def calculate_volatility(values):
    """Calculate trade volatility (coefficient of variation)"""
    if len(values) < 2 or all(v == 0 for v in values):
        return 0
    
    mean_val = np.mean(values)
    if mean_val == 0:
        return 0
    
    std_dev = np.std(values)
    cv = (std_dev / mean_val) * 100  # Coefficient of variation in percentage
    
    return round(cv, 2)


def get_trend_direction(values):
    """Determine if trend is up or down"""
    if len(values) < 2:
        return "Insufficient data"
    
    recent_avg = np.mean(values[-3:]) if len(values) >= 3 else values[-1]
    previous_avg = np.mean(values[:3]) if len(values) >= 3 else values[0]
    
    if previous_avg == 0:
        return "New entry"
    
    change_pct = ((recent_avg - previous_avg) / previous_avg) * 100
    
    if change_pct > 20:
        return "📈 Strong Uptrend"
    elif change_pct > 5:
        return "📊 Moderate Uptrend"
    elif change_pct > -5:
        return "→ Stable"
    elif change_pct > -20:
        return "📉 Moderate Downtrend"
    else:
        return "📉 Sharp Downtrend"


def get_peak_value(values, years):
    """Get peak trade value and year"""
    if not values or not years:
        return None, None
    
    max_idx = values.index(max(values))
    return max(values), years[max_idx]


def calculate_market_share(country_values, total_values):
    """Calculate market share percentage"""
    if not total_values or sum(total_values) == 0:
        return 0
    
    return (sum(country_values) / sum(total_values)) * 100 if country_values else 0


def get_top_countries_share(partners_data, limit=5):
    """Get top countries and their combined market share"""
    if not partners_data:
        return 0
    
    top_countries = get_top_countries(partners_data, limit)
    total_top = sum(float(c.get("2024-2025", c.get("2023-2024", 0)) or 0) for c in top_countries)
    
    # Get all values
    all_values = sum(float(c.get("2024-2025", c.get("2023-2024", 0)) or 0) for c in partners_data)
    
    if all_values == 0:
        return 0
    
    return (total_top / all_values) * 100


def analyze_growth_distribution(partners_data):
    """Analyze growth rates across partners"""
    growth_rates = []
    
    for partner in partners_data:
        current = float(partner.get("2024-2025", 0) or 0)
        previous = float(partner.get("2023-2024", 0) or 0)
        
        if previous > 0:
            growth = ((current - previous) / previous) * 100
            growth_rates.append(growth)
    
    if not growth_rates:
        return {"avg_growth": 0, "max_growth": 0, "min_growth": 0}
    
    return {
        "avg_growth": np.mean(growth_rates),
        "max_growth": max(growth_rates),
        "min_growth": min(growth_rates),
        "positive_count": sum(1 for g in growth_rates if g > 0),
        "negative_count": sum(1 for g in growth_rates if g < 0)
    }
