"""
Digital Twin Thermal Management - Cooling Analytics Page
Provides deep inspection of the dual-fan forced-convection cooling subsystem,
including heat dissipation effectiveness, inlet-outlet Delta-T, COP, fan curves, and prescriptive recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.kpi_cards import render_kpi_card, render_simulated_notice
from components.charts import (
    create_cooling_performance_chart,
    create_component_comparison_bar,
)
from data.simulated_data import (
    get_cooling_analytics_metrics,
    get_cooling_recommendations,
    get_current_component_metrics,
    COMPONENTS,
)


def render_cooling_analytics_page():
    """Renders the Cooling Analytics and Thermal Management Subsystem page."""
    telemetry_history = st.session_state.get("telemetry_history")
    latest_record = telemetry_history.iloc[-1].to_dict() if telemetry_history is not None else {}
    cooling_metrics = get_cooling_analytics_metrics(latest_record)
    comp_df = get_current_component_metrics(ambient_temp=latest_record.get("ambient_temp", 24.5))

    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.5rem;">❄️ Cooling Subsystem Analytics & Aerodynamics</h2>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:2px;">
                    Dual-Fan PWM Closed-Loop • Airflow Mass Balance • Thermal Resistance & COP Tracking
                </div>
            </div>
            <span class="sim-badge" style="background:rgba(6,182,212,0.15); border-color:rgba(6,182,212,0.4); color:#38bdf8;">
                AERODYNAMIC LOOP
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top KPI Metrics Row
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            render_kpi_card(
                title="Cooling Status",
                value="ACTIVE",
                unit="PWM",
                delta="74% Duty Cycle",
                delta_type="neutral",
                status_tag="Nominal",
                status_type="normal",
                icon="❄️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            render_kpi_card(
                title="Airflow Temp Rise",
                value=f"{cooling_metrics['delta_t']:.1f}",
                unit="°C",
                delta=f"{cooling_metrics['inlet_temp']:.1f}°C → {cooling_metrics['outlet_temp']:.1f}°C",
                delta_type="neutral",
                status_tag="ΔT Nominal",
                status_type="normal",
                icon="🌡️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            render_kpi_card(
                title="Chassis Airflow",
                value=f"{cooling_metrics['airflow_cfm']:.1f}",
                unit="CFM",
                delta=f"{cooling_metrics['mass_flow_kg_s']:.4f} kg/s",
                delta_type="up-good",
                status_tag="Forced Convection",
                status_type="normal",
                icon="💨",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            render_kpi_card(
                title="Heat Rejected",
                value=f"{cooling_metrics['heat_dissipated_w']:.0f}",
                unit="W",
                delta=f"Air: {cooling_metrics['air_absorbed_heat_w']:.0f} W",
                delta_type="neutral",
                status_tag="Steady State",
                status_type="normal",
                icon="⚡",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            render_kpi_card(
                title="Cooling COP",
                value=f"{cooling_metrics['cooling_cop']:.2f}",
                unit="Eff.",
                delta=f"{cooling_metrics['fan_electrical_power_w']:.1f}W Fan Draw",
                delta_type="up-good",
                status_tag="High COP",
                status_type="normal",
                icon="🎯",
                card_type="success",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Primary Analytics Charts: Cooling Performance Over Time + Component Comparison
    col_chart_left, col_chart_right = st.columns([1.5, 1])

    with col_chart_left:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom:0;">
                <div class="card-header-bar">
                    <span class="card-title">📈 Cooling Subsystem Response Waveform</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">FAN RPM vs AIRFLOW ΔT</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if telemetry_history is not None:
            fig_perf = create_cooling_performance_chart(telemetry_history, height=360)
            st.plotly_chart(fig_perf, use_container_width=True, key="cooling_perf_chart")

    with col_chart_right:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom:0;">
                <div class="card-header-bar">
                    <span class="card-title">📊 Component Thermal Margins Under Airflow</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">ACTIVE FORCED COOLING</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_comp = create_component_comparison_bar(comp_df, height=360)
        st.plotly_chart(fig_comp, use_container_width=True, key="cooling_comp_bar")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Cooling Health & Aerodynamic Diagnostic Parameters
    col_diag1, col_diag2 = st.columns([1.2, 1.3])

    with col_diag1:
        st.markdown(
            f"""
            <div class="industrial-card">
                <div class="card-header-bar">
                    <span class="card-title">⚙️ Subsystem Thermodynamic Parameters</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#38bdf8;">DIAGNOSTIC TELEMETRY</span>
                </div>
                <div style="display:flex; flex-direction:column; gap:0.7rem; font-size:0.85rem;">
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.35rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Primary Fan Array 1:</span>
                        <strong style="color:#f8fafc; font-family:'JetBrains Mono',monospace;">{cooling_metrics['fan_1_rpm']} RPM (PWM 72%)</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.35rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Secondary Fan Array 2:</span>
                        <strong style="color:#f8fafc; font-family:'JetBrains Mono',monospace;">{cooling_metrics['fan_2_rpm']} RPM (PWM 69%)</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.35rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Inlet Cool Air Intake:</span>
                        <strong style="color:#38bdf8; font-family:'JetBrains Mono',monospace;">{cooling_metrics['inlet_temp']:.1f} °C</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.35rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Exhaust Heated Air Outlet:</span>
                        <strong style="color:#fb923c; font-family:'JetBrains Mono',monospace;">{cooling_metrics['outlet_temp']:.1f} °C</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:0.35rem; border-bottom:1px solid rgba(148,163,184,0.08);">
                        <span style="color:#94a3b8;">Effective Thermal Resistance:</span>
                        <strong style="color:#34d399; font-family:'JetBrains Mono',monospace;">{cooling_metrics['thermal_resistance_k_w']:.3f} K/W</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:#94a3b8;">Fan Power Draw:</span>
                        <strong style="color:#cbd5e1; font-family:'JetBrains Mono',monospace;">{cooling_metrics['fan_electrical_power_w']:.1f} W (Total Dual)</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_diag2:
        recs = get_cooling_recommendations(cooling_metrics, comp_df)
        recs_html = ""
        for r in recs:
            p_color = "#ef4444" if r["priority"] == "HIGH" else ("#f59e0b" if r["priority"] == "MEDIUM" else "#10b981")
            recs_html += f"""
            <div style="background:rgba(17,24,39,0.7); border-left:3px solid {p_color}; border-radius:6px; padding:0.65rem 0.85rem; margin-bottom:0.5rem; font-size:0.825rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem;">
                    <strong style="color:#f1f5f9;">{r['target']}</strong>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; font-weight:700; color:{p_color};">[{r['priority']} PRIORITY]</span>
                </div>
                <div style="color:#cbd5e1; line-height:1.4;">{r['recommendation']}</div>
                <div style="font-size:0.7rem; color:#64748b; margin-top:0.25rem;">Category: {r['type']}</div>
            </div>
            """

        st.markdown(
            f"""
            <div class="industrial-card">
                <div class="card-header-bar">
                    <span class="card-title">💡 Digital Twin Prescriptive Cooling Recommendations</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#34d399;">ACTIONABLE ADVICE</span>
                </div>
                {recs_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_simulated_notice(
        "Thermodynamic mass-balance and cooling effectiveness metrics are calculated using illustrative physical fluid and heat transfer equations."
    )

