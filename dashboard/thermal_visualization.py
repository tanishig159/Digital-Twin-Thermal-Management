"""
Digital Twin Thermal Management - Thermal Visualization Page
Renders high-fidelity 2D engineering thermal heatmaps and 3D surface meshes of the electronic enclosure,
with component overlays, isotherm contours, hotspot highlighting, and localized component thermal inspection.
"""

import streamlit as st
import numpy as np
import pandas as pd

from components.kpi_cards import render_kpi_card, render_simulated_notice
from components.charts import create_thermal_heatmap, create_3d_thermal_surface
from data.simulated_data import (
    COMPONENTS,
    CHASSIS_WIDTH_MM,
    CHASSIS_HEIGHT_MM,
    generate_enclosure_thermal_field,
    get_current_component_metrics,
)


def render_thermal_visualization_page():
    """Renders the 2D/3D engineering thermal simulation page."""
    # Retrieve telemetry context
    telemetry_history = st.session_state.get("telemetry_history")
    latest_record = telemetry_history.iloc[-1].to_dict() if telemetry_history is not None else {}
    ambient_temp = latest_record.get("ambient_temp", 24.5)

    st.markdown(
        """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
            <div>
                <h2 style="margin:0; font-size:1.5rem;">🗺️ Electronic Enclosure Thermal Field Visualization</h2>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:2px;">
                    Chassis Spatial Heat Distribution • 300 × 200 mm Physical Form Factor • Forced Convective Drift
                </div>
            </div>
            <span class="sim-badge">Simulated Thermal Mesh</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Visualization Controls Toolbar
    with st.container():
        st.markdown(
            """
            <div class="industrial-card" style="padding: 0.85rem 1.25rem; margin-bottom: 1rem;">
                <div style="font-size:0.75rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.6rem;">
                    Visualization Engineering Controls
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([1.2, 1.2, 1, 1, 1.2])

        with col_c1:
            view_mode = st.selectbox(
                "Display Mode",
                ["2D Contour Heatmap", "3D Thermal Surface Mesh"],
                index=0,
                key="thermal_view_mode",
            )

        with col_c2:
            colorscale = st.selectbox(
                "Color Gradient Palette",
                ["Turbo", "Thermal", "Jet", "Plasma", "Inferno"],
                index=0,
                key="thermal_colorscale",
            )

        with col_c3:
            show_components = st.checkbox("Show Components", value=True, key="thermal_show_comps")

        with col_c4:
            show_contours = st.checkbox("Show Isotherms", value=True, key="thermal_show_contours")

        with col_c5:
            hotspot_thresh = st.slider(
                "Hotspot Highlight (°C)",
                min_value=60.0,
                max_value=95.0,
                value=78.0,
                step=1.0,
                key="thermal_hotspot_thresh",
            )

    # Generate or load spatial mesh
    # Cache mesh in session state or generate
    x_mesh, y_mesh, temp_grid = generate_enclosure_thermal_field(
        ambient_temp=ambient_temp,
        load_multiplier=1.05,
        cooling_factor=1.0,
        nx=80,
        ny=55,
        add_noise=True,
    )

    min_mesh_t = float(np.min(temp_grid))
    max_mesh_t = float(np.max(temp_grid))
    avg_mesh_t = float(np.mean(temp_grid))
    hotspot_area_pct = round(float(np.sum(temp_grid >= hotspot_thresh) / temp_grid.size * 100), 1)

    # Quick summary row
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    with c_kpi1:
        st.markdown(
            render_kpi_card(
                title="Enclosure Peak Temp",
                value=f"{max_mesh_t:.1f}",
                unit="°C",
                status_tag="Peak Hotspot",
                status_type="warning" if max_mesh_t >= 78 else "normal",
                icon="🔥",
                card_type="warning" if max_mesh_t >= 78 else "normal",
            ),
            unsafe_allow_html=True,
        )
    with c_kpi2:
        st.markdown(
            render_kpi_card(
                title="Enclosure Min Temp",
                value=f"{min_mesh_t:.1f}",
                unit="°C",
                status_tag="Inlet Air Zone",
                status_type="normal",
                icon="❄️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )
    with c_kpi3:
        st.markdown(
            render_kpi_card(
                title="Mean Chassis Temp",
                value=f"{avg_mesh_t:.1f}",
                unit="°C",
                status_tag="Bulk Mean",
                status_type="normal",
                icon="🌡️",
                card_type="normal",
            ),
            unsafe_allow_html=True,
        )
    with c_kpi4:
        st.markdown(
            render_kpi_card(
                title="Elevated Area Ratio",
                value=f"{hotspot_area_pct}",
                unit="%",
                status_tag=f"T ≥ {hotspot_thresh:.0f}°C",
                status_type="warning" if hotspot_area_pct > 5 else "normal",
                icon="📐",
                card_type="warning" if hotspot_area_pct > 5 else "normal",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Main Visual Plot Area
    if view_mode == "2D Contour Heatmap":
        fig_heat = create_thermal_heatmap(
            x=x_mesh,
            y=y_mesh,
            temp_grid=temp_grid,
            show_components=show_components,
            show_contours=show_contours,
            show_hotspots=True,
            threshold_c=hotspot_thresh,
            colorscale=colorscale,
            height=520,
        )
        st.plotly_chart(fig_heat, use_container_width=True, key="main_thermal_heatmap")
    else:
        fig_surface = create_3d_thermal_surface(
            x=x_mesh,
            y=y_mesh,
            temp_grid=temp_grid,
            colorscale=colorscale,
            height=540,
        )
        st.plotly_chart(fig_surface, use_container_width=True, key="main_thermal_surface")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Component Inspector & Spatial Coordinate Explorer
    st.markdown(
        """
        <div class="industrial-card">
            <div class="card-header-bar">
                <span class="card-title">🔍 Localized Component Thermal Inspector</span>
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#64748b;">SPATIAL ZONE AUDIT</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    comp_df = get_current_component_metrics(ambient_temp=ambient_temp)

    col_insp1, col_insp2 = st.columns([1, 2])

    with col_insp1:
        comp_choices = [c.name for c in COMPONENTS.values()]
        selected_name = st.selectbox("Select Component to Inspect", comp_choices, key="inspect_comp_select")
        
        # Find chosen component
        selected_comp = next(c for c in COMPONENTS.values() if c.name == selected_name)
        comp_row = comp_df[comp_df["id"] == selected_comp.id].iloc[0]

        st.markdown(
            f"""
            <div style="background:rgba(15,23,42,0.8); border:1px solid rgba(148,163,184,0.15); border-radius:8px; padding:1rem; font-size:0.85rem; line-height:1.7;">
                <div><strong>Category:</strong> <span style="color:#38bdf8;">{selected_comp.category}</span></div>
                <div><strong>Current Peak Temp:</strong> <span style="color:{comp_row['status_color']}; font-weight:700; font-family:'JetBrains Mono',monospace;">{comp_row['temperature_c']} °C</span></div>
                <div><strong>Operating Limit:</strong> <span style="font-family:'JetBrains Mono',monospace;">{selected_comp.max_rating_c} °C</span></div>
                <div><strong>Thermal Safety Margin:</strong> <span style="color:{comp_row['status_color']}; font-weight:600; font-family:'JetBrains Mono',monospace;">{comp_row['margin_c']} °C</span></div>
                <div><strong>Power Dissipation:</strong> <span style="font-family:'JetBrains Mono',monospace;">{comp_row['power_w']} W</span></div>
                <div><strong>Physical Footprint:</strong> <span style="font-family:'JetBrains Mono',monospace;">{selected_comp.width:.0f} × {selected_comp.height:.0f} mm</span></div>
                <div><strong>Center Coordinates:</strong> <span style="font-family:'JetBrains Mono',monospace;">({selected_comp.center[0]:.1f}, {selected_comp.center[1]:.1f}) mm</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_insp2:
        st.markdown(
            """
            <div style="font-size:0.85rem; font-weight:600; color:#cbd5e1; margin-bottom:0.5rem;">
                All Monitored Enclosure Thermal Zones
            </div>
            """,
            unsafe_allow_html=True,
        )
        display_table = comp_df[["component", "temperature_c", "warning_threshold_c", "max_rating_c", "margin_c", "status", "power_w"]].copy()
        display_table.columns = ["Component Zone", "Temp (°C)", "Warn Limit (°C)", "Max Limit (°C)", "Margin (°C)", "Health Status", "Power (W)"]
        
        st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
        )

    render_simulated_notice(
        "Heatmap is generated using 2D conduction-convection multi-source Gaussian diffusion models with aerodynamic intake-to-exhaust thermal drift."
    )

