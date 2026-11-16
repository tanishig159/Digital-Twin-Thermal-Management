"""
Digital Twin Thermal Management - What-If Simulation Page
Provides interactive sliders for Heat Load, Ambient Temperature, Cooling Intensity,
and Convection Coefficient, updating illustrative thermal states, comparative bar charts, and 2D heatmaps.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.kpi_cards import render_kpi_card, render_simulated_notice
from components.charts import (
    create_what_if_comparison_chart,
    create_thermal_heatmap,
)
from data.simulated_data import (
    COMPONENTS,
    simulate_what_if_scenario,
    generate_enclosure_thermal_field,
)


def render_what_if_simulation_page():
    """Renders the What-If Thermal Scenario Simulator page."""
    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.5rem;">🧪 What-If Thermal Scenario Simulation</h2>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:2px;">
                    Parametric Sensitivity Engine • Interactive Boundary Condition Modulation • Baseline vs Stress Comparison
                </div>
            </div>
            <span class="sim-badge" style="background:rgba(168,85,247,0.15); border-color:rgba(168,85,247,0.4); color:#c084fc;">
                PARAMETRIC DEMONSTRATOR
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simulation Disclaimer Box
    st.markdown(
        """
        <div class="info-callout" style="border-color: rgba(168, 85, 247, 0.35); background: rgba(168, 85, 247, 0.08); color: #e9d5ff;">
            <span style="font-size:1.2rem;">⚡</span>
            <div>
                <strong>DEMONSTRATION CALCULATION NOTICE:</strong>
                Outputs below are calculated using a simplified algebraic-convective demonstration model to illustrate digital twin interactive capabilities.
                <strong>These are NOT certified ANSYS FEA solvers or trained ML surrogate inferences.</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Scenario Quick Presets
    st.markdown(
        """
        <div style="font-size:0.75rem; font-weight:700; color:#64748b; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.5rem;">
            Quick Engineering Scenario Presets
        </div>
        """,
        unsafe_allow_html=True,
    )

    p_col1, p_col2, p_col3, p_col4 = st.columns(4)

    # Initialize preset values in session state if not set
    if "sim_heat_load" not in st.session_state:
        st.session_state["sim_heat_load"] = 210.0
    if "sim_ambient_temp" not in st.session_state:
        st.session_state["sim_ambient_temp"] = 25.0
    if "sim_cooling_pct" not in st.session_state:
        st.session_state["sim_cooling_pct"] = 70.0
    if "sim_convection_h" not in st.session_state:
        st.session_state["sim_convection_h"] = 35.0

    with p_col1:
        if st.button("🟢 Nominal Baseline", use_container_width=True, key="preset_nominal"):
            st.session_state["sim_heat_load"] = 210.0
            st.session_state["sim_ambient_temp"] = 25.0
            st.session_state["sim_cooling_pct"] = 70.0
            st.session_state["sim_convection_h"] = 35.0
            st.rerun()

    with p_col2:
        if st.button("🏜️ Desert / High Ambient", use_container_width=True, key="preset_desert"):
            st.session_state["sim_heat_load"] = 230.0
            st.session_state["sim_ambient_temp"] = 42.0
            st.session_state["sim_cooling_pct"] = 85.0
            st.session_state["sim_convection_h"] = 40.0
            st.rerun()

    with p_col3:
        if st.button("⚡ Max Workload Stress", use_container_width=True, key="preset_stress"):
            st.session_state["sim_heat_load"] = 380.0
            st.session_state["sim_ambient_temp"] = 30.0
            st.session_state["sim_cooling_pct"] = 90.0
            st.session_state["sim_convection_h"] = 55.0
            st.rerun()

    with p_col4:
        if st.button("⚠️ Cooling Fan Degradation", use_container_width=True, key="preset_degrade"):
            st.session_state["sim_heat_load"] = 260.0
            st.session_state["sim_ambient_temp"] = 28.0
            st.session_state["sim_cooling_pct"] = 25.0
            st.session_state["sim_convection_h"] = 12.0
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Interactive Sliders Panel
    with st.container():
        st.markdown(
            """
            <div class="industrial-card" style="padding: 0.85rem 1.25rem; margin-bottom: 1.25rem;">
                <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.6rem;">
                    🎛️ Parametric Boundary Condition Controls
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)

        with col_s1:
            heat_load = st.slider(
                "Total Heat Load (W)",
                min_value=50.0,
                max_value=500.0,
                value=float(st.session_state["sim_heat_load"]),
                step=10.0,
                key="slider_heat_load",
                help="Cumulative electrical heat power generated by all internal enclosure electronics.",
            )
            st.session_state["sim_heat_load"] = heat_load

        with col_s2:
            ambient_t = st.slider(
                "Ambient Temperature (°C)",
                min_value=15.0,
                max_value=45.0,
                value=float(st.session_state["sim_ambient_temp"]),
                step=1.0,
                key="slider_ambient_temp",
                help="External environmental temperature entering the enclosure intake.",
            )
            st.session_state["sim_ambient_temp"] = ambient_t

        with col_s3:
            cooling_pct = st.slider(
                "Cooling Intensity (%)",
                min_value=10.0,
                max_value=100.0,
                value=float(st.session_state["sim_cooling_pct"]),
                step=5.0,
                key="slider_cooling_pct",
                help="PWM duty cycle modulating dual-fan rotational speed and volumetric airflow.",
            )
            st.session_state["sim_cooling_pct"] = cooling_pct

        with col_s4:
            convection_h = st.slider(
                "Convection Coeff. h (W/m²K)",
                min_value=5.0,
                max_value=150.0,
                value=float(st.session_state["sim_convection_h"]),
                step=5.0,
                key="slider_convection_h",
                help="Heat transfer coefficient governing forced convective boundary dissipation.",
            )
            st.session_state["sim_convection_h"] = convection_h

    # Run the Demonstration What-If Calculation
    sim_result = simulate_what_if_scenario(
        heat_load_w=heat_load,
        ambient_temp_c=ambient_t,
        cooling_intensity_pct=cooling_pct,
        convection_coeff_h=convection_h,
    )

    sim_df = sim_result["components_df"]
    max_sim_t = sim_result["max_temperature_c"]
    avg_sim_t = sim_result["avg_temperature_c"]
    hotspots = sim_result["hotspot_count"]
    status_str = sim_result["system_status"]
    status_color = sim_result["system_status_color"]

    # Comparative KPI Metrics Row (Baseline vs Simulated Condition)
    c1, c2, c3, c4 = st.columns(4)

    # Baseline nominal max was ~80.4°C
    delta_max = round(max_sim_t - 80.4, 1)
    delta_avg = round(avg_sim_t - 64.2, 1)

    with c1:
        st.markdown(
            render_kpi_card(
                title="Simulated Max Temp",
                value=f"{max_sim_t:.1f}",
                unit="°C",
                delta=f"{delta_max:+.1f}°C vs Nominal",
                delta_type="up-bad" if delta_max > 0 else "down-good",
                status_tag="Elevated" if max_sim_t >= 85 else "Safe",
                status_type="warning" if max_sim_t >= 85 else "normal",
                icon="🔥",
                card_type="critical" if max_sim_t >= 95 else ("warning" if max_sim_t >= 85 else "normal"),
            ),
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            render_kpi_card(
                title="Simulated Mean Temp",
                value=f"{avg_sim_t:.1f}",
                unit="°C",
                delta=f"{delta_avg:+.1f}°C vs Nominal",
                delta_type="up-bad" if delta_avg > 0 else "down-good",
                status_tag="Enclosure Mean",
                status_type="normal",
                icon="🌡️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            render_kpi_card(
                title="Predicted Hotspots",
                value=f"{hotspots}",
                unit="Zones",
                delta=f"{hotspots} Exceeding Limits",
                delta_type="up-bad" if hotspots > 0 else "down-good",
                status_tag="Critical" if hotspots > 1 else ("Warning" if hotspots == 1 else "Zero"),
                status_type="critical" if hotspots > 1 else ("warning" if hotspots == 1 else "normal"),
                icon="⚠️",
                card_type="critical" if hotspots > 1 else ("warning" if hotspots == 1 else "success"),
            ),
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            render_kpi_card(
                title="Thermal Envelope Status",
                value=f"{status_str}",
                unit="",
                delta=f"h = {convection_h:.0f} W/m²K",
                delta_type="neutral",
                status_tag="Simulation",
                status_type="normal" if "SAFE" in status_str else ("warning" if "WARNING" in status_str else "critical"),
                icon="🛡️",
                card_type="normal" if "SAFE" in status_str else ("warning" if "WARNING" in status_str else "critical"),
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Visual Comparison: Grouped Comparison Chart + Simulated 2D Thermal Heatmap
    col_c1, col_c2 = st.columns([1.2, 1.2])

    with col_c1:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom:0;">
                <div class="card-header-bar">
                    <span class="card-title">📊 Baseline vs Simulated Operating Conditions</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">COMPONENT-BY-COMPONENT</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_comp = create_what_if_comparison_chart(sim_df, height=440)
        st.plotly_chart(fig_comp, use_container_width=True, key="whatif_comp_chart")

    with col_c2:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom:0;">
                <div class="card-header-bar">
                    <span class="card-title">🗺️ Simulated 2D Thermal Field (Modulated)</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#a78bfa;">DEMONSTRATION MESH</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_heat = create_thermal_heatmap(
            x=sim_result["x_mesh"],
            y=sim_result["y_mesh"],
            temp_grid=sim_result["temp_field"],
            show_components=True,
            show_contours=True,
            show_hotspots=True,
            threshold_c=78.0,
            title="<b>Simulated Operating Heatmap</b> under user sliders",
            height=440,
        )
        st.plotly_chart(fig_heat, use_container_width=True, key="whatif_heatmap_chart")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Detailed Delta Headroom Table
    st.markdown(
        """
        <div class="industrial-card">
            <div class="card-header-bar">
                <span class="card-title">📋 Parametric Thermal Sensitivity Breakdown</span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">DELTA vs NOMINAL</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    table_df = sim_df[["component", "baseline_temp_c", "simulated_temp_c", "delta_c", "warning_threshold_c", "max_rating_c", "margin_c", "status"]].copy()
    table_df.columns = ["Component", "Baseline (°C)", "Simulated (°C)", "Δ Change (°C)", "Warn Limit (°C)", "Max Rating (°C)", "Margin (°C)", "Status"]

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    render_simulated_notice(
        "Demonstration model updates instantly via algebraic thermal network approximations. Ready for ANSYS surrogate reduced-order models (ROMs) in Phase 2."
    )

