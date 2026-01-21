"""
Professional chart styling for Trade Dashboard
Applies consistent, eye-pleasing Plotly configurations
"""

# Color scheme - Professional and accessible
COLORS = {
    "primary": "#0066cc",      # Professional blue
    "success": "#00a86b",      # Green
    "warning": "#ff9800",      # Orange
    "danger": "#ff6b6b",       # Red
    "info": "#00bcd4",         # Cyan
    "secondary": "#9c27b0",    # Purple
    "light": "#f5f5f5",        # Light gray
    "dark": "#2c3e50",         # Dark blue
}

EXPORT_COLOR = "#0066cc"   # Blue for exports
IMPORT_COLOR = "#ff6b6b"   # Red for imports
CATEGORY_COLORS = [
    "#0066cc", "#00a86b", "#ff9800", "#ff6b6b", 
    "#9c27b0", "#00bcd4", "#f39c12", "#1abc9c",
    "#3498db", "#e74c3c", "#2ecc71", "#f1c40f"
]


def get_base_layout():
    """Base layout for all charts - professional and clean"""
    return {
        "font": {"family": "Arial, sans-serif", "size": 12, "color": "#2c3e50"},
        "plot_bgcolor": "#ffffff",
        "paper_bgcolor": "#ffffff",
        "margin": {"l": 70, "r": 30, "t": 40, "b": 60},
        "hovermode": "x unified",
        "showlegend": True,
        "legend": {
            "orientation": "v",
            "yanchor": "top",
            "y": 0.99,
            "xanchor": "right",
            "x": 0.99,
            "bgcolor": "rgba(255, 255, 255, 0.8)",
            "bordercolor": "#ddd",
            "borderwidth": 1,
        },
    }


def style_bar_chart(fig, title="", title_color=COLORS["primary"]):
    """Apply professional styling to bar charts"""
    fig.update_layout(
        **get_base_layout(),
        title={
            "text": title,
            "font": {"size": 18, "color": title_color, "family": "Arial Black"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis={"showgrid": False, "showline": True, "linewidth": 1, "linecolor": "#ddd"},
        yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": "#f0f0f0", "showline": True, "linewidth": 1},
    )
    
    fig.update_traces(
        marker=dict(line=dict(width=0.5, color="white")),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>"
    )
    
    return fig


def style_line_chart(fig, title="", title_color=COLORS["primary"]):
    """Apply professional styling to line charts"""
    fig.update_layout(
        **get_base_layout(),
        title={
            "text": title,
            "font": {"size": 18, "color": title_color, "family": "Arial Black"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis={"showgrid": False, "showline": True, "linewidth": 1, "linecolor": "#ddd"},
        yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": "#f0f0f0", "showline": True, "linewidth": 1},
    )
    
    fig.update_traces(
        line=dict(width=2.5),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>"
    )
    
    return fig


def style_area_chart(fig, title="", title_color=COLORS["primary"]):
    """Apply professional styling to area charts"""
    fig.update_layout(
        **get_base_layout(),
        title={
            "text": title,
            "font": {"size": 18, "color": title_color, "family": "Arial Black"},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis={"showgrid": False, "showline": True, "linewidth": 1, "linecolor": "#ddd"},
        yaxis={"showgrid": True, "gridwidth": 1, "gridcolor": "#f0f0f0", "showline": True, "linewidth": 1},
    )
    
    fig.update_traces(
        line=dict(width=2),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>"
    )
    
    return fig


def style_indicator(fig, title=""):
    """Apply professional styling to indicator cards"""
    fig.update_layout(
        font={"family": "Arial", "size": 14, "color": "#2c3e50"},
        paper_bgcolor="#ffffff",
        margin={"l": 10, "r": 10, "t": 40, "b": 10},
        height=250,
    )
    
    return fig


def get_export_import_colors(trade_type):
    """Get color based on trade type"""
    if isinstance(trade_type, str):
        if trade_type.upper() == "EXPORT":
            return EXPORT_COLOR
        elif trade_type.upper() == "IMPORT":
            return IMPORT_COLOR
    return COLORS["primary"]


def apply_professional_theme(fig, chart_type="bar", title=""):
    """Apply professional theme to any chart"""
    if chart_type == "bar":
        return style_bar_chart(fig, title)
    elif chart_type == "line":
        return style_line_chart(fig, title)
    elif chart_type == "area":
        return style_area_chart(fig, title)
    elif chart_type == "indicator":
        return style_indicator(fig, title)
    
    return fig
