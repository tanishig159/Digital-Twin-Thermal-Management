"""
Digital Twin Thermal Management - Industrial KPI Cards & UI Badges
Provides reusable rendering functions for modern industrial telemetry cards,
health status banners, and thermal alert lists.
"""

from typing import Optional, List, Dict, Any
import streamlit as st


def render_kpi_card(
    title: str,
    value: str or float or int,
    unit: str = "",
    delta: Optional[str] = None,
    delta_type: str = "neutral",  # "up-bad", "up-good", "down-good", "down-bad", "neutral"
    status_tag: Optional[str] = None,
    status_type: str = "normal",  # "normal", "warning", "critical"
    icon: str = "⚡",
    card_type: str = "normal",  # "normal", "warning", "critical", "success"
) -> str:
    """
    Renders a premium industrial telemetry KPI card with accent borders,
    high-contrast typography, and status indicators.
    """
    delta_html = ""
    if delta:
        arrow = "↑" if "up" in delta_type else ("↓" if "down" in delta_type else "•")
        delta_html = f'<div class="kpi-delta {delta_type}"><span>{arrow}</span> {delta}</div>'

    tag_html = ""
    if status_tag:
        tag_html = f'<div class="kpi-status-tag tag-{status_type}">{status_tag}</div>'

    html = f"""
    <div class="kpi-card {card_type}">
        <div class="kpi-top">
            <span class="kpi-title">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value-wrap">
            <span class="kpi-value">{value}</span>
            <span class="kpi-unit">{unit}</span>
        </div>
        <div class="kpi-footer">
            {delta_html}
            {tag_html}
        </div>
    </div>
    """
    return html


def render_system_health_banner(
    overall_status: str,
    status_type: str,
    max_temp: float,
    active_hotspots: int,
    cooling_mode: str = "Closed-Loop Adaptive PWM",
    sync_latency_ms: int = 18,
):
    """
    Renders the prominent top-level digital twin health banner.
    """
    dot_class = status_type.lower()
    pill_class = status_type.lower()
    
    status_text = {
        "normal": "SYSTEM HEALTHY & SYNCHRONIZED",
        "warning": "THERMAL ADVISORY - ELEVATED ZONE",
        "critical": "CRITICAL THERMAL ALERT - ACTION REQUIRED",
    }.get(status_type, "MONITORING ACTIVE")

    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="dashboard-title-group">
                <div style="display:flex; align-items:center; gap: 0.75rem;">
                    <h1>Digital Twin Thermal Management</h1>
                    <span class="sim-badge">Simulated Model</span>
                </div>
                <div class="dashboard-subtitle">
                    <span>Target Enclosure: <strong>ET-402 Industrial Avionics / Power Unit</strong></span>
                    <span>•</span>
                    <span>Dimensions: <strong>300 × 200 mm</strong></span>
                    <span>•</span>
                    <span>Twin Sync: <strong>{sync_latency_ms} ms Latency</strong></span>
                </div>
            </div>
            <div>
                <div class="twin-status-pill {pill_class}">
                    <span class="status-dot {dot_class}"></span>
                    <span>{status_text}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert_box(alerts: List[Dict[str, str]]):
    """
    Renders styled alert items list.
    """
    items_html = ""
    for a in alerts:
        severity = a.get("severity", "info")
        icon = "🔴" if severity == "critical" else ("🟡" if severity == "warning" else "🔵")
        items_html += f"""
        <div class="alert-item {severity}">
            <div style="display:flex; align-items:flex-start; gap:0.6rem;">
                <span style="font-size:0.9rem;">{icon}</span>
                <div>
                    <div style="font-weight:600; color:#f1f5f9;">{a['component']}: <span style="font-weight:400; color:#cbd5e1;">{a['message']}</span></div>
                    <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.2rem;">Action: {a.get('action', 'Monitor telemetry')}</div>
                </div>
            </div>
            <div class="alert-meta">
                <span>{a.get('time', '--:--:--')}</span>
            </div>
        </div>
        """

    st.markdown(
        f"""
        <div class="industrial-card">
            <div class="card-header-bar">
                <span class="card-title">🚨 Recent Thermal Events & Telemetry Alerts</span>
                <span style="font-size:0.75rem; color:#64748b; font-family:'JetBrains Mono',monospace;">REAL-TIME LOG</span>
            </div>
            {items_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_simulated_notice(message: str = "All telemetry, spatial gradients, and thermal predictions are SIMULATED for demonstration purposes."):
    """
    Renders a clear simulation disclaimer bar.
    """
    st.markdown(
        f"""
        <div class="info-callout">
            <span style="font-size:1.1rem;">ℹ️</span>
            <div>
                <strong>SIMULATION NOTICE:</strong> {message}
                <div style="font-size:0.75rem; color:#94a3b8; margin-top:2px;">
                    Modular architecture is staged for ANSYS Fluent/Icepak, Reduced-Order ROMs, and real physical edge sensors.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

