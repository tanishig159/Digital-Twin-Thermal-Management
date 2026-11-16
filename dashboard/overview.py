"""
Digital Twin Thermal Management - System Overview Page
Main mission-control dashboard with top KPI cards, temperature trend chart,
component temperature ranking, recent thermal events, and enclosure operating telemetry.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.kpi_cards import render_kpi_card, render_system_health_banner, render_alert_box, render_simulated_notice
from components.charts import (
    create_temperature_trend_chart,
    create_component_comparison_bar,
    create_cooling_performance_chart,
)
from data.simulated_data import (
    get_current_component_metrics,
    get_recent_thermal_alerts,
    get_cooling_analytics_metrics,
)


def render_overview_page():
    """Renders the comprehensive System Overview dashboard."""
    # Retrieve telemetry from session state
    telemetry_history = st.session_state.get("telemetry_history")
    latest_record = telemetry_history.iloc[-1].to_dict() if telemetry_history is not None else {}

    # Current component metrics
    comp_df = get_current_component_metrics(
        ambient_temp=latest_record.get("ambient_temp", 24.5),
        load_multiplier=1.05,
        cooling_factor=1.0,
    )

    # Calculate top metrics
    max_temp = float(comp_df["temperature_c"].max())
    avg_temp = round(float(comp_df["temperature_c"].mean()), 1)
    ambient_temp = latest_record.get("ambient_temp", 24.5)
    hotspots = comp_df[comp_df["temperature_c"] >= comp_df["warning_threshold_c"]]
    hotspot_count = len(hotspots)
    critical_count = len(comp_df[comp_df["temperature_c"] >= comp_df["max_rating_c"]])

    # Determine overall status
    if critical_count > 0:
        overall_status = "CRITICAL ALERT"
        status_type = "critical"
    elif hotspot_count > 0:
        overall_status = "WARNING"
        status_type = "warning"
    else:
        overall_status = "NORMAL"
        status_type = "normal"

    # 1. System Health Banner
    render_system_health_banner(
        overall_status=overall_status,
        status_type=status_type,
        max_temp=max_temp,
        active_hotspots=hotspot_count,
    )

    # 2. Top KPI Cards Row
    cooling_metrics = get_cooling_analytics_metrics(latest_record)
    fan_speed = latest_record.get("fan_1_rpm", 3450)
    fan_status = f"{fan_speed:,} RPM ({round(fan_speed/4800*100)}%)"

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        max_card_type = "critical" if max_temp >= 90 else ("warning" if max_temp >= 78 else "normal")
        st.markdown(
            render_kpi_card(
                title="Max Temperature",
                value=f"{max_temp:.1f}",
                unit="°C",
                delta="+1.6°C vs 1h avg",
                delta_type="up-bad" if max_temp > 75 else "neutral",
                status_tag="Elevated" if max_temp >= 78 else "Nominal",
                status_type="warning" if max_temp >= 78 else "normal",
                icon="🔥",
                card_type=max_card_type,
            ),
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            render_kpi_card(
                title="Average Temp",
                value=f"{avg_temp:.1f}",
                unit="°C",
                delta="+0.8°C drift",
                delta_type="neutral",
                status_tag="Normal Range",
                status_type="normal",
                icon="🌡️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            render_kpi_card(
                title="Ambient (Inlet)",
                value=f"{ambient_temp:.1f}",
                unit="°C",
                delta="Stable ±0.2°C",
                delta_type="neutral",
                status_tag="Intake Nom.",
                status_type="normal",
                icon="💨",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with col4:
        hotspot_card_type = "critical" if critical_count > 0 else ("warning" if hotspot_count > 0 else "success")
        st.markdown(
            render_kpi_card(
                title="Active Hotspots",
                value=f"{hotspot_count}",
                unit="Zones",
                delta=f"{critical_count} Critical" if critical_count > 0 else "0 Exceeding Max",
                delta_type="up-bad" if hotspot_count > 0 else "down-good",
                status_tag="Action Req." if critical_count > 0 else ("Watch" if hotspot_count > 0 else "Clear"),
                status_type="critical" if critical_count > 0 else ("warning" if hotspot_count > 0 else "normal"),
                icon="⚠️",
                card_type=hotspot_card_type,
            ),
            unsafe_allow_html=True,
        )

    with col5:
        st.markdown(
            render_kpi_card(
                title="Cooling Status",
                value=f"{fan_status}",
                unit="",
                delta=f"ΔT: {cooling_metrics['delta_t']}°C",
                delta_type="neutral",
                status_tag="Active PWM",
                status_type="normal",
                icon="❄️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Primary Charts Row: Telemetry Trend + Component Comparison
    col_chart_left, col_chart_right = st.columns([1.5, 1])

    with col_chart_left:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom: 0;">
                <div class="card-header-bar">
                    <span class="card-title">📈 Real-Time Multi-Component Thermal History</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">PAST 60 MINUTES (1m INTERVAL)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if telemetry_history is not None:
            fig_trend = create_temperature_trend_chart(telemetry_history, height=360)
            st.plotly_chart(fig_trend, use_container_width=True, key="overview_trend_chart")

    with col_chart_right:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom: 0;">
                <div class="card-header-bar">
                    <span class="card-title">📊 Component Thermal Ranking & Headroom</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">CURRENT INSTANT</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_bars = create_component_comparison_bar(comp_df, height=360)
        st.plotly_chart(fig_bars, use_container_width=True, key="overview_bars_chart")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 4. Enclosure Operating Status & Recent Thermal Alerts
    col_stat_left, col_stat_right = st.columns([1.1, 1.4])

    with col_stat_left:
        st.markdown(
            """
            <div class="industrial-card">
                <div class="card-header-bar">
                    <span class="card-title">⚙️ Enclosure Operating Subsystem Telemetry</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#38bdf8;">SIMULATED TELEMETRY</span>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.75rem; font-size:0.85rem;">
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.4rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Total Heat Dissipation:</span>
                        <strong style="color:#f8fafc; font-family:'JetBrains Mono',monospace;">{heat_diss:.1f} W</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.4rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Chassis Forced Airflow:</span>
                        <strong style="color:#38bdf8; font-family:'JetBrains Mono',monospace;">{airflow:.1f} CFM ({mass_flow:.4f} kg/s)</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.4rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Intake / Exhaust Differential:</span>
                        <strong style="color:#fb923c; font-family:'JetBrains Mono',monospace;">ΔT {delta_t:.1f} °C ({inlet:.1f}°C → {outlet:.1f}°C)</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.4rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">System Thermal Resistance (R_th):</span>
                        <strong style="color:#34d399; font-family:'JetBrains Mono',monospace;">{r_th:.3f} K/W</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.4rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Cooling Subsystem COP:</span>
                        <strong style="color:#a78bfa; font-family:'JetBrains Mono',monospace;">{cop:.2f} (Eff: Nominal)</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8;">Fan Array 1 / 2 Speeds:</span>
                        <strong style="color:#cbd5e1; font-family:'JetBrains Mono',monospace;">{fan1} / {fan2} RPM</strong>
                    </div>
                </div>
            </div>
            """.format(
                heat_diss=cooling_metrics["heat_dissipated_w"],
                airflow=cooling_metrics["airflow_cfm"],
                mass_flow=cooling_metrics["mass_flow_kg_s"],
                delta_t=cooling_metrics["delta_t"],
                inlet=cooling_metrics["inlet_temp"],
                outlet=cooling_metrics["outlet_temp"],
                r_th=cooling_metrics["thermal_resistance_k_w"],
                cop=cooling_metrics["cooling_cop"],
                fan1=cooling_metrics["fan_1_rpm"],
                fan2=cooling_metrics["fan_2_rpm"],
            ),
            unsafe_allow_html=True,
        )

    with col_stat_right:
        alerts = get_recent_thermal_alerts(comp_df)
        render_alert_box(alerts)

    # Simulation Notice Footer
    render_simulated_notice(
        "Demonstration data powered by synthetic physical multi-source heat diffusion and transient first-order convective lag models."
    )

