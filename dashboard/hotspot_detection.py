"""
Digital Twin Thermal Management - Hotspot Detection Page
Provides thermal hotspot identification, configurable warning/critical thresholds,
dynamic component temperature ranking, temperature distribution histograms, and risk mitigations.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.kpi_cards import render_kpi_card, render_simulated_notice
from components.charts import (
    create_component_comparison_bar,
    create_temperature_distribution_chart,
    create_thermal_heatmap,
)
from data.simulated_data import (
    COMPONENTS,
    get_current_component_metrics,
    generate_enclosure_thermal_field,
)


def render_hotspot_detection_page():
    """Renders the Hotspot Detection and Thermal Risk Analysis page."""
    telemetry_history = st.session_state.get("telemetry_history")
    latest_record = telemetry_history.iloc[-1].to_dict() if telemetry_history is not None else {}
    ambient_temp = latest_record.get("ambient_temp", 24.5)

    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.5rem;">🔥 Hotspot Detection & Thermal Stress Audit</h2>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:2px;">
                    Peak Isotherm Tracking • Dynamic Threshold Sensitivity • Thermal Headroom Analysis
                </div>
            </div>
            <span class="sim-badge" style="background:rgba(245,158,11,0.15); border-color:rgba(245,158,11,0.4); color:#fbbf24;">
                CRITICAL ZONE AUDITOR
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Configurable Threshold Controls
    with st.container():
        st.markdown(
            """
            <div class="industrial-card" style="padding: 0.85rem 1.25rem; margin-bottom: 1rem;">
                <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.5rem;">
                    Configurable Hotspot Classification Thresholds
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_t1, col_t2, col_t3 = st.columns([1.5, 1.5, 1])

        with col_t1:
            warn_threshold = st.slider(
                "Advisory Warning Threshold (°C)",
                min_value=60.0,
                max_value=90.0,
                value=76.0,
                step=1.0,
                key="hotspot_warn_slider",
                help="Components reaching this temperature trigger elevated cooling and logging.",
            )

        with col_t2:
            crit_threshold = st.slider(
                "Emergency Critical Threshold (°C)",
                min_value=75.0,
                max_value=105.0,
                value=88.0,
                step=1.0,
                key="hotspot_crit_slider",
                help="Components exceeding this temperature trigger immediate throttling.",
            )

        with col_t3:
            st.markdown(
                f"""
                <div style="padding-top:0.6rem; font-size:0.75rem; color:#94a3b8; line-height:1.5;">
                    <div>Active Warn: <strong style="color:#fbbf24; font-family:'JetBrains Mono',monospace;">{warn_threshold:.1f} °C</strong></div>
                    <div>Active Crit: <strong style="color:#f87171; font-family:'JetBrains Mono',monospace;">{crit_threshold:.1f} °C</strong></div>
                    <div>Safe Band: <strong style="color:#34d399; font-family:'JetBrains Mono',monospace;">&lt; {warn_threshold:.1f} °C</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Fetch component metrics and re-evaluate with current user thresholds
    comp_df = get_current_component_metrics(ambient_temp=ambient_temp, load_multiplier=1.06)

    # Dynamic status reassessment based on user sliders
    comp_df["warning_threshold_c"] = warn_threshold
    comp_df["max_rating_c"] = crit_threshold
    comp_df["margin_c"] = np.round(crit_threshold - comp_df["temperature_c"], 1)

    normal_comps = comp_df[comp_df["temperature_c"] < warn_threshold]
    warning_comps = comp_df[(comp_df["temperature_c"] >= warn_threshold) & (comp_df["temperature_c"] < crit_threshold)]
    critical_comps = comp_df[comp_df["temperature_c"] >= crit_threshold]

    normal_count = len(normal_comps)
    warning_count = len(warning_comps)
    critical_count = len(critical_comps)
    total_hotspots = warning_count + critical_count

    # Top KPI summary cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            render_kpi_card(
                title="Total Hotspots",
                value=f"{total_hotspots}",
                unit="Zones",
                delta=f"{critical_count} Critical / {warning_count} Warning",
                delta_type="up-bad" if total_hotspots > 0 else "down-good",
                status_tag="Needs Action" if critical_count > 0 else ("Watch" if warning_count > 0 else "Optimal"),
                status_type="critical" if critical_count > 0 else ("warning" if warning_count > 0 else "normal"),
                icon="🔥",
                card_type="critical" if critical_count > 0 else ("warning" if total_hotspots > 0 else "success"),
            ),
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            render_kpi_card(
                title="Critical Zones",
                value=f"{critical_count}",
                unit="Nodes",
                delta=f"Threshold: ≥ {crit_threshold:.0f}°C",
                delta_type="neutral",
                status_tag="Critical" if critical_count > 0 else "Zero",
                status_type="critical" if critical_count > 0 else "normal",
                icon="🚨",
                card_type="critical" if critical_count > 0 else "normal",
            ),
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            render_kpi_card(
                title="Warning Zones",
                value=f"{warning_count}",
                unit="Nodes",
                delta=f"Threshold: ≥ {warn_threshold:.0f}°C",
                delta_type="neutral",
                status_tag="Advisory" if warning_count > 0 else "Zero",
                status_type="warning" if warning_count > 0 else "normal",
                icon="⚠️",
                card_type="warning" if warning_count > 0 else "normal",
            ),
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            render_kpi_card(
                title="Normal Zones",
                value=f"{normal_count}",
                unit="Nodes",
                delta=f"Safe Margin: &lt; {warn_threshold:.0f}°C",
                delta_type="neutral",
                status_tag="Compliant",
                status_type="normal",
                icon="✅",
                card_type="success",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Visual Charts: Ranked Comparison Bar + Spatial Distribution Histogram
    col_c1, col_c2 = st.columns([1.2, 1])

    with col_c1:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom:0;">
                <div class="card-header-bar">
                    <span class="card-title">📊 Ranked Component Thermal Headroom</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">DYNAMIC THRESHOLDS</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        fig_bar = create_component_comparison_bar(
            comp_df,
            threshold_warning=warn_threshold,
            threshold_critical=crit_threshold,
            height=370,
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="hotspot_rank_chart")

    with col_c2:
        st.markdown(
            """
            <div class="industrial-card" style="margin-bottom:0;">
                <div class="card-header-bar">
                    <span class="card-title">📉 Enclosure Spatial Thermal Distribution</span>
                    <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">MESH HISTOGRAM</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _, _, temp_grid = generate_enclosure_thermal_field(
            ambient_temp=ambient_temp,
            load_multiplier=1.06,
            cooling_factor=1.0,
            nx=70,
            ny=45,
        )
        fig_dist = create_temperature_distribution_chart(
            temp_grid,
            threshold_warning=warn_threshold,
            threshold_critical=crit_threshold,
            height=370,
        )
        st.plotly_chart(fig_dist, use_container_width=True, key="hotspot_dist_chart")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Detailed Hotspot Assessment Table & Visual Indicators
    st.markdown(
        """
        <div class="industrial-card">
            <div class="card-header-bar">
                <span class="card-title">🎯 Component Hotspot Audit & Mitigation Assessment</span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">ZONE-BY-ZONE HEADROOM</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Update status tags for table
    table_rows = []
    for _, row in comp_df.iterrows():
        t = row["temperature_c"]
        if t >= crit_threshold:
            st_text = "CRITICAL 🔴"
            action = "Immediate thermal throttling recommended"
        elif t >= warn_threshold:
            st_text = "WARNING 🟡"
            action = "Increase targeted airflow velocity via Fan Array 2"
        else:
            st_text = "NORMAL 🟢"
            action = "Operating within nominal design envelope"

        table_rows.append({
            "Component Zone": row["component"],
            "Measured Temp (°C)": t,
            "Threshold Limit (°C)": crit_threshold,
            "Safety Headroom (°C)": round(crit_threshold - t, 1),
            "Status Classification": st_text,
            "Prescriptive Mitigation": action,
        })

    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    render_simulated_notice(
        "Hotspot detection thresholds are dynamically evaluated against simulated telemetry and chassis thermal fields."
    )

