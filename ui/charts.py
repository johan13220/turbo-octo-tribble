"""Reusable Plotly chart builders. All functions return plotly.graph_objects.Figure."""
from __future__ import annotations

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from core.models import AuditReport, BacklinkSummary, CompetitorSnapshot, GSCDataPoint, Keyword


def keyword_scatter(keywords: list[Keyword]) -> go.Figure:
    """Scatter: search volume vs difficulty, color by position band."""
    if not keywords:
        return _empty("No keyword data available")

    df = pd.DataFrame([k.model_dump() for k in keywords])
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    df["search_volume"] = pd.to_numeric(df["search_volume"], errors="coerce").fillna(0)
    df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce").fillna(0)

    def _band(pos):
        if pos is None or pd.isna(pos):
            return "Unknown"
        if pos <= 3:
            return "1-3"
        if pos <= 10:
            return "4-10"
        if pos <= 20:
            return "11-20"
        return "21+"

    df["band"] = df["position"].apply(_band)
    color_map = {"1-3": "#00c853", "4-10": "#69f0ae", "11-20": "#ffd740", "21+": "#ff6d00", "Unknown": "#bdbdbd"}

    fig = px.scatter(
        df,
        x="difficulty",
        y="search_volume",
        color="band",
        hover_name="keyword",
        hover_data={"position": True, "cpc": True},
        color_discrete_map=color_map,
        labels={"difficulty": "Keyword Difficulty", "search_volume": "Search Volume", "band": "Position"},
        title="Keywords: Volume vs Difficulty",
    )
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    fig.update_layout(height=400, margin=dict(t=50, b=40))
    return fig


def position_histogram(keywords: list[Keyword]) -> go.Figure:
    """Bar chart of keyword counts by position band."""
    if not keywords:
        return _empty("No keyword data available")

    bands = {"1-3": 0, "4-10": 0, "11-20": 0, "21+": 0}
    for kw in keywords:
        pos = kw.position
        if pos is None:
            continue
        if pos <= 3:
            bands["1-3"] += 1
        elif pos <= 10:
            bands["4-10"] += 1
        elif pos <= 20:
            bands["11-20"] += 1
        else:
            bands["21+"] += 1

    colors = ["#00c853", "#69f0ae", "#ffd740", "#ff6d00"]
    fig = go.Figure(go.Bar(
        x=list(bands.keys()),
        y=list(bands.values()),
        marker_color=colors,
        text=list(bands.values()),
        textposition="outside",
    ))
    fig.update_layout(
        title="Keyword Distribution by Position",
        xaxis_title="Position Band",
        yaxis_title="Number of Keywords",
        height=350,
        margin=dict(t=50, b=40),
    )
    return fig


def audit_gauge(score: float) -> go.Figure:
    """Gauge indicator for site health score 0-100."""
    color = "#00c853" if score >= 80 else "#ffd740" if score >= 50 else "#f44336"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Site Health Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 50], "color": "#ffebee"},
                {"range": [50, 80], "color": "#fff9c4"},
                {"range": [80, 100], "color": "#e8f5e9"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 2},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(height=300, margin=dict(t=30, b=10))
    return fig


def competitor_bar(snapshots: list[CompetitorSnapshot], metric: str = "organic_traffic") -> go.Figure:
    """Horizontal bar comparing a metric across competitor domains."""
    if not snapshots:
        return _empty("No competitor data available")

    labels = {
        "organic_traffic": "Organic Traffic",
        "organic_keywords": "Organic Keywords",
        "authority_score": "Authority Score",
    }
    values = [getattr(s, metric) or 0 for s in snapshots]
    domains = [s.domain for s in snapshots]

    fig = go.Figure(go.Bar(
        x=values,
        y=domains,
        orientation="h",
        marker_color="#1976d2",
        text=values,
        textposition="outside",
    ))
    fig.update_layout(
        title=f"Competitor Comparison — {labels.get(metric, metric)}",
        xaxis_title=labels.get(metric, metric),
        height=max(300, len(snapshots) * 60),
        margin=dict(t=50, b=40),
    )
    return fig


def gsc_performance_chart(data_points: list[GSCDataPoint]) -> go.Figure:
    """Dual-axis line chart: clicks + impressions over time, with avg position."""
    if not data_points:
        return _empty("No performance data available")

    dates = [p.date for p in data_points]
    clicks = [p.clicks for p in data_points]
    impressions = [p.impressions for p in data_points]
    positions = [p.position for p in data_points]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=clicks, name="Clicks",
        line=dict(color="#1976d2", width=2),
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=impressions, name="Impressions",
        line=dict(color="#90caf9", width=2, dash="dot"),
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=positions, name="Avg Position",
        line=dict(color="#f57c00", width=2),
        yaxis="y2",
    ))
    fig.update_layout(
        title="Search Performance Over Time",
        height=380,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Clicks / Impressions"),
        yaxis2=dict(
            title="Avg Position",
            overlaying="y",
            side="right",
            autorange="reversed",
            showgrid=False,
        ),
    )
    return fig


def _empty(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=14, color="gray"))
    fig.update_layout(height=300, xaxis_visible=False, yaxis_visible=False)
    return fig
