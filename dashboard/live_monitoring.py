"""
Digital Twin Thermal Management - Live Monitoring Page
Simulates real-time telemetry streaming for CPU, Power Module (VRM), Battery,
Motor Controller, and Ambient sensor nodes, with rolling trend graphs and stream controls.
"""

from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np

from components.kpi_cards import render_kpi_card, render_simulated_notice
from components.charts import create_temperature_trend_chart
from data.simulated_data import (
    COMPONENTS,
    simulate_telemetry_step,
    generate_historical_telemetry,
)


def render_live_monitoring_page():
    """Renders the Live Telemetry Monitoring page."""
    # Ensure telemetry history exists in session state
    if "telemetry_history" not in st.session_state:
        st.session_state["telemetry_history"] = generate_historical_telemetry(n_points=60)

    history_df = st.session_state["telemetry_history"]
    latest = history_df.iloc[-1].to_dict()

    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.5rem;">⚡ Real-Time Telemetry & Live Sensor Streams</h2>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:2px;">
                    Edge Telemetry Loop • Dynamic Time-Series Ingestion • Multi-Node Thermal Tracking
                </div>
            </div>
            <span class="sim-badge" style="background:rgba(239,68,68,0.15); border-color:rgba(239,68,68,0.4); color:#f87171;">
                ● LIVE SIMULATION STREAM
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Telemetry Control Deck
    with st.container():
        st.markdown(
            """
            <div class="industrial-card" style="padding: 0.85rem 1.25rem; margin-bottom: 1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em;">
                        Telemetry Stream Controls
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#94a3b8;">
                        Buffer Size: {buf_len} points | Latest: {latest_time}
                    </div>
                </div>
            </div>
            """.format(
                buf_len=len(history_df),
                latest_time=latest["timestamp"].strftime("%H:%M:%S") if isinstance(latest["timestamp"], datetime) else str(latest["timestamp"]),
            ),
            unsafe_allow_html=True,
        )

        col_b1, col_b2, col_b3, col_b4 = st.columns([1.2, 1.2, 1, 1.5])

        with col_b1:
            if st.button("⏩ Simulate Next Reading Step", use_container_width=True, key="btn_sim_step"):
                new_row = simulate_telemetry_step(history_df.iloc[-1])
                # Append and keep sliding window of 90 points
                new_df = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
                if len(new_df) > 90:
                    new_df = new_df.iloc[-90:].reset_index(drop=True)
                st.session_state["telemetry_history"] = new_df
                st.rerun()

        with col_b2:
            if st.button("🔄 Reset Stream History", use_container_width=True, key="btn_reset_stream"):
                st.session_state["telemetry_history"] = generate_historical_telemetry(n_points=60)
                st.rerun()

        with col_b3:
            noise_intensity = st.selectbox(
                "Noise / Fluctuation",
                ["Low (0.2°C)", "Standard (0.4°C)", "Dynamic Stress (0.8°C)"],
                index=1,
                key="stream_noise_select",
            )

        with col_b4:
            st.markdown(
                """
                <div style="padding-top:0.4rem; font-size:0.75rem; color:#94a3b8; text-align:right;">
                    Stream Status: <strong style="color:#34d399;">CONNECTED (Simulated)</strong><br>
                    Packet Loss: <strong style="color:#f8fafc; font-family:'JetBrains Mono',monospace;">0.00%</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Component-wise Live Readings Cards
    # Explicitly requested: CPU, Power Module (VRM), Battery Module, Motor/Controller, Ambient
    c1, c2, c3, c4, c5 = st.columns(5)

    cpu_temp = latest.get("cpu_temp", 71.5)
    vrm_temp = latest.get("vrm_temp", 78.2)
    battery_temp = latest.get("battery_temp", 43.8)
    inverter_temp = latest.get("inverter_temp", 80.4)
    ambient_temp = latest.get("ambient_temp", 24.5)

    with c1:
        cpu_status = "critical" if cpu_temp >= 95 else ("warning" if cpu_temp >= 78 else "normal")
        st.markdown(
            render_kpi_card(
                title="CPU / SoC Core",
                value=f"{cpu_temp:.1f}",
                unit="°C",
                delta=f"Max: 95°C",
                delta_type="neutral",
                status_tag=cpu_status.upper(),
                status_type=cpu_status,
                icon="💻",
                card_type=cpu_status,
            ),
            unsafe_allow_html=True,
        )

    with c2:
        vrm_status = "critical" if vrm_temp >= 105 else ("warning" if vrm_temp >= 85 else "normal")
        st.markdown(
            render_kpi_card(
                title="Power Module (VRM)",
                value=f"{vrm_temp:.1f}",
                unit="°C",
                delta="Max: 105°C",
                delta_type="neutral",
                status_tag=vrm_status.upper(),
                status_type=vrm_status,
                icon="⚡",
                card_type=vrm_status,
            ),
            unsafe_allow_html=True,
        )

    with c3:
        battery_status = "critical" if battery_temp >= 60 else ("warning" if battery_temp >= 48 else "normal")
        st.markdown(
            render_kpi_card(
                title="Battery Module",
                value=f"{battery_temp:.1f}",
                unit="°C",
                delta="Max: 60°C",
                delta_type="neutral",
                status_tag=battery_status.upper(),
                status_type=battery_status,
                icon="🔋",
                card_type=battery_status,
            ),
            unsafe_allow_html=True,
        )

    with c4:
        inverter_status = "critical" if inverter_temp >= 90 else ("warning" if inverter_temp >= 76 else "normal")
        st.markdown(
            render_kpi_card(
                title="Motor Controller",
                value=f"{inverter_temp:.1f}",
                unit="°C",
                delta="Max: 90°C",
                delta_type="neutral",
                status_tag=inverter_status.upper(),
                status_type=inverter_status,
                icon="⚙️",
                card_type=inverter_status,
            ),
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            render_kpi_card(
                title="Ambient Sensor",
                value=f"{ambient_temp:.1f}",
                unit="°C",
                delta="Inlet Flow",
                delta_type="neutral",
                status_tag="NOMINAL",
                status_type="normal",
                icon="🌐",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Interactive Trend Graph with Component Filter Multi-select
    st.markdown(
        """
        <div class="industrial-card" style="margin-bottom:0;">
            <div class="card-header-bar">
                <span class="card-title">📈 Rolling Telemetry Waveform Analysis</span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">SIMULATED TIME-SERIES</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_components = list(COMPONENTS.keys())
    selected_components = st.multiselect(
        "Filter Monitored Component Channels",
        options=all_components,
        default=all_components,
        format_func=lambda cid: f"{COMPONENTS[cid].short_name} ({cid.upper()})",
        key="live_telemetry_filter",
    )

    if not selected_components:
        selected_components = all_components

    fig_live_trend = create_temperature_trend_chart(
        history_df,
        selected_components=selected_components,
        height=400,
    )
    st.plotly_chart(fig_live_trend, use_container_width=True, key="live_trend_plot")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Recent Telemetry Table
    st.markdown(
        """
        <div class="industrial-card">
            <div class="card-header-bar">
                <span class="card-title">📋 Raw Telemetry Frames (Latest Ingested Packets)</span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">SLIDING BUFFER</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Format table for display
    display_df = history_df.tail(8).iloc[::-1].copy()
    display_df["timestamp"] = display_df["timestamp"].apply(
        lambda t: t.strftime("%H:%M:%S") if isinstance(t, datetime) else str(t)
    )

    cols_to_show = ["timestamp", "ambient_temp", "cpu_temp", "vrm_temp", "inverter_temp", "battery_temp", "fan_1_rpm", "chassis_airflow_cfm", "outlet_temp"]
    display_df = display_df[cols_to_show]
    display_df.columns = ["Time", "Ambient (°C)", "CPU (°C)", "VRM (°C)", "Inverter (°C)", "Battery (°C)", "Fan 1 (RPM)", "Airflow (CFM)", "Outlet (°C)"]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    render_simulated_notice(
        "Telemetry stream simulated using physical first-order thermal lag equations with stochastic noise injection. Hardware IoT communication layer ready."
    )

