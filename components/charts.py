"""
Digital Twin Thermal Management - Industrial Plotly Charts & Visualizations
Provides reusable interactive Plotly charts with consistent industrial dark themes,
engineering contour heatmaps, 3D thermal surfaces, telemetry trends, and cooling analytics.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from data.simulated_data import COMPONENTS, ThermalComponent, CHASSIS_WIDTH_MM, CHASSIS_HEIGHT_MM


# Common styling theme constants
CHART_FONT_FAMILY = "Plus Jakarta Sans, -apple-system, sans-serif"
MONO_FONT_FAMILY = "JetBrains Mono, monospace"
GRID_COLOR = "rgba(148, 163, 184, 0.12)"
AXIS_LINE_COLOR = "rgba(148, 163, 184, 0.25)"
TEXT_COLOR = "#cbd5e1"
PLOT_BG = "#0f172a"
PAPER_BG = "rgba(0,0,0,0)"

COLOR_MAP = {
    "cpu": "#38bdf8",       # Sky cyan
    "vrm": "#fb923c",       # Orange
    "inverter": "#f87171",  # Soft red
    "battery": "#34d399",   # Emerald
    "ddr5": "#a78bfa",      # Lavender/Purple
    "transformer": "#eab308", # Amber
    "ambient": "#94a3b8",   # Slate
}


def _apply_dark_theme(fig: go.Figure, height: int = 400) -> go.Figure:
    """Applies common dark industrial styling to any Plotly figure."""
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family=CHART_FONT_FAMILY, color=TEXT_COLOR, size=12),
        margin=dict(l=45, r=30, t=45, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=12,
            font_family=MONO_FONT_FAMILY,
            bordercolor="rgba(148, 163, 184, 0.3)",
        ),
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=AXIS_LINE_COLOR,
        tickfont=dict(family=MONO_FONT_FAMILY, size=11, color="#94a3b8"),
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=AXIS_LINE_COLOR,
        tickfont=dict(family=MONO_FONT_FAMILY, size=11, color="#94a3b8"),
    )
    return fig


# -----------------------------------------------------------------------------
# 1. 2D Thermal Heatmap with Component Overlay & Hotspots
# -----------------------------------------------------------------------------
def create_thermal_heatmap(
    x: np.ndarray,
    y: np.ndarray,
    temp_grid: np.ndarray,
    show_components: bool = True,
    show_contours: bool = True,
    show_hotspots: bool = True,
    threshold_c: float = 78.0,
    colorscale: str = "Turbo",
    title: Optional[str] = None,
    height: int = 480,
) -> go.Figure:
    """
    Renders an engineering-grade 2D thermal heatmap representing the electronic enclosure.
    Includes component bounding boxes, labels, airflow vectors, and hotspot callouts.
    """
    fig = go.Figure()

    # Base Heatmap layer
    fig.add_trace(
        go.Heatmap(
            x=x,
            y=y,
            z=temp_grid,
            colorscale=colorscale,
            colorbar=dict(
                title=dict(
                    text="Temp (°C)",
                    font=dict(family=MONO_FONT_FAMILY, size=12, color=TEXT_COLOR),
                    side="right",
                ),
                tickfont=dict(family=MONO_FONT_FAMILY, size=11, color=TEXT_COLOR),
                thickness=16,
                len=0.95,
                outlinecolor="rgba(148, 163, 184, 0.2)",
                outlinewidth=1,
            ),
            hovertemplate=(
                "<b>Position:</b> (%{x:.1f}, %{y:.1f}) mm<br>"
                "<b>Surface Temp:</b> %{z:.1f} °C"
                "<extra></extra>"
            ),
            zsmooth="best",
        )
    )

    # Optional contour isolines overlay (isotherms)
    if show_contours:
        min_t, max_t = float(np.min(temp_grid)), float(np.max(temp_grid))
        step = max(2.0, round((max_t - min_t) / 8.0, 1))
        fig.add_trace(
            go.Contour(
                x=x,
                y=y,
                z=temp_grid,
                showscale=False,
                contours=dict(
                    start=min_t,
                    end=max_t,
                    size=step,
                    coloring="none",
                ),
                line=dict(color="rgba(255, 255, 255, 0.22)", width=1, dash="dot"),
                hoverinfo="skip",
            )
        )

    # Component boundaries & annotations
    if show_components:
        for comp_id, comp in COMPONENTS.items():
            cx, cy = comp.center
            # Semi-transparent component bounding box
            fig.add_shape(
                type="rect",
                x0=comp.x_min,
                x1=comp.x_max,
                y0=comp.y_min,
                y1=comp.y_max,
                line=dict(color="#38bdf8", width=1.8, dash="solid"),
                fillcolor="rgba(15, 23, 42, 0.4)",
            )
            # Component Label
            fig.add_annotation(
                x=cx,
                y=cy,
                text=f"<b>{comp.short_name}</b>",
                showarrow=False,
                font=dict(family=CHART_FONT_FAMILY, size=10, color="#ffffff"),
                bgcolor="rgba(15, 23, 42, 0.75)",
                bordercolor="rgba(56, 189, 248, 0.5)",
                borderwidth=1,
                borderpad=3,
                opacity=0.95,
            )

    # Highlight Hotspots exceeding threshold
    if show_hotspots:
        # Detect local regions in grid above threshold
        hotspot_mask = temp_grid >= threshold_c
        if np.any(hotspot_mask):
            # Find coordinates of top hotspots
            y_indices, x_indices = np.where(hotspot_mask)
            # Subsample if too dense to avoid marker clutter
            step = max(1, len(x_indices) // 12)
            hot_x = x[x_indices[::step]]
            hot_y = y[y_indices[::step]]
            hot_z = temp_grid[y_indices[::step], x_indices[::step]]

            # Pulsing target rings
            fig.add_trace(
                go.Scatter(
                    x=hot_x,
                    y=hot_y,
                    mode="markers",
                    marker=dict(
                        symbol="circle-open-dot",
                        size=14,
                        color="#ef4444",
                        line=dict(color="#ffffff", width=2),
                    ),
                    name="Hotspot Warning",
                    hovertemplate=(
                        "<b>HOTSPOT PEAK:</b> %{z:.1f} °C<br>"
                        "Location: (%{x:.1f}, %{y:.1f}) mm"
                        "<extra></extra>"
                    ),
                    customdata=hot_z,
                )
            )

    # Airflow intake & exhaust indicators
    fig.add_annotation(
        x=15,
        y=100,
        text="<b>INLET AIRFLOW ➔</b><br><span style='font-size:9px'>25°C Cool Intake</span>",
        showarrow=False,
        font=dict(family=CHART_FONT_FAMILY, size=10, color="#38bdf8"),
        bgcolor="rgba(15, 23, 42, 0.8)",
        bordercolor="#0284c7",
        borderwidth=1,
        borderpad=4,
    )
    fig.add_annotation(
        x=285,
        y=100,
        text="<b>➔ EXHAUST</b><br><span style='font-size:9px'>Heated Air Exit</span>",
        showarrow=False,
        font=dict(family=CHART_FONT_FAMILY, size=10, color="#fb923c"),
        bgcolor="rgba(15, 23, 42, 0.8)",
        bordercolor="#ea580c",
        borderwidth=1,
        borderpad=4,
    )

    # Layout details
    fig.update_layout(
        title=dict(
            text=title or "<b>Electronic Enclosure 2D Thermal Simulation Field</b> (300 × 200 mm)",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
            y=0.98,
        ),
        xaxis=dict(
            title="Chassis X-Axis (mm)",
            range=[0, CHASSIS_WIDTH_MM],
            gridcolor=GRID_COLOR,
            tickmode="linear",
            tick0=0,
            dtick=50,
        ),
        yaxis=dict(
            title="Chassis Y-Axis (mm)",
            range=[0, CHASSIS_HEIGHT_MM],
            scaleanchor="x",
            scaleratio=1,
            gridcolor=GRID_COLOR,
            tickmode="linear",
            tick0=0,
            dtick=50,
        ),
        showlegend=False,
    )

    return _apply_dark_theme(fig, height=height)


# -----------------------------------------------------------------------------
# 2. 3D Thermal Surface Plot
# -----------------------------------------------------------------------------
def create_3d_thermal_surface(
    x: np.ndarray,
    y: np.ndarray,
    temp_grid: np.ndarray,
    colorscale: str = "Turbo",
    height: int = 500,
) -> go.Figure:
    """
    Renders an interactive 3D thermal elevation surface mesh.
    """
    fig = go.Figure(
        data=[
            go.Surface(
                x=x,
                y=y,
                z=temp_grid,
                colorscale=colorscale,
                colorbar=dict(
                    title=dict(text="Temp (°C)", font=dict(family=MONO_FONT_FAMILY, size=11, color=TEXT_COLOR)),
                    tickfont=dict(family=MONO_FONT_FAMILY, size=10, color=TEXT_COLOR),
                    thickness=14,
                    len=0.8,
                ),
                hovertemplate="X: %{x:.1f} mm<br>Y: %{y:.1f} mm<br>Temp: <b>%{z:.1f} °C</b><extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="<b>3D Thermal Elevation Surface Model (Digital Twin Mesh)</b>",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
            y=0.98,
        ),
        scene=dict(
            xaxis=dict(title="X (mm)", gridcolor=GRID_COLOR, backgroundcolor=PLOT_BG),
            yaxis=dict(title="Y (mm)", gridcolor=GRID_COLOR, backgroundcolor=PLOT_BG),
            zaxis=dict(title="Temp (°C)", gridcolor=GRID_COLOR, backgroundcolor=PLOT_BG),
            camera=dict(eye=dict(x=-1.5, y=-1.6, z=1.2)),
        ),
    )

    return _apply_dark_theme(fig, height=height)


# -----------------------------------------------------------------------------
# 3. Multi-Component Time-Series Telemetry Trend
# -----------------------------------------------------------------------------
def create_temperature_trend_chart(
    telemetry_df: pd.DataFrame,
    selected_components: Optional[List[str]] = None,
    threshold_warning: float = 78.0,
    threshold_critical: float = 90.0,
    height: int = 380,
) -> go.Figure:
    """
    Renders multi-line temperature telemetry over time with limit lines.
    """
    fig = go.Figure()

    if selected_components is None:
        selected_components = list(COMPONENTS.keys())

    # Add each component trace
    for comp_id in selected_components:
        col = f"{comp_id}_temp"
        if col in telemetry_df.columns:
            comp_name = COMPONENTS[comp_id].short_name if comp_id in COMPONENTS else comp_id
            color = COLOR_MAP.get(comp_id, "#38bdf8")
            fig.add_trace(
                go.Scatter(
                    x=telemetry_df["timestamp"],
                    y=telemetry_df[col],
                    mode="lines",
                    name=comp_name,
                    line=dict(color=color, width=2.2),
                    hovertemplate=f"<b>{comp_name}:</b> %{{y:.1f}} °C<extra></extra>",
                )
            )

    # Ambient trace
    if "ambient_temp" in telemetry_df.columns:
        fig.add_trace(
            go.Scatter(
                x=telemetry_df["timestamp"],
                y=telemetry_df["ambient_temp"],
                mode="lines",
                name="Ambient (Inlet)",
                line=dict(color="#64748b", width=1.5, dash="dash"),
                hovertemplate="<b>Ambient:</b> %{y:.1f} °C<extra></extra>",
            )
        )

    # Threshold horizontal reference lines
    fig.add_hline(
        y=threshold_critical,
        line_dash="dot",
        line_color="#ef4444",
        line_width=1.5,
        annotation_text="Critical Limit (90°C)",
        annotation_position="top right",
        annotation_font=dict(color="#ef4444", size=10, family=MONO_FONT_FAMILY),
    )
    fig.add_hline(
        y=threshold_warning,
        line_dash="dot",
        line_color="#f59e0b",
        line_width=1.5,
        annotation_text="Warning Threshold (78°C)",
        annotation_position="bottom right",
        annotation_font=dict(color="#f59e0b", size=10, family=MONO_FONT_FAMILY),
    )

    fig.update_layout(
        title=dict(
            text="<b>Real-Time Component Temperature Telemetry Trend</b>",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
        ),
        xaxis=dict(title="Timestamp", showgrid=True),
        yaxis=dict(title="Temperature (°C)", showgrid=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
    )

    return _apply_dark_theme(fig, height=height)


# -----------------------------------------------------------------------------
# 4. Component Temperature Comparison & Thermal Margin Bar Chart
# -----------------------------------------------------------------------------
def create_component_comparison_bar(
    comp_df: pd.DataFrame,
    threshold_warning: float = 78.0,
    threshold_critical: float = 90.0,
    height: int = 340,
) -> go.Figure:
    """
    Renders horizontal ranked bar chart of components colored by status.
    """
    df_sorted = comp_df.sort_values(by="temperature_c", ascending=True)

    colors = []
    for temp in df_sorted["temperature_c"]:
        if temp >= threshold_critical:
            colors.append("#ef4444")
        elif temp >= threshold_warning:
            colors.append("#f59e0b")
        else:
            colors.append("#06b6d4")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=df_sorted["short_name"],
            x=df_sorted["temperature_c"],
            orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.15)", width=1)),
            text=[f" {t:.1f} °C (Margin: {m:.1f}°C)" for t, m in zip(df_sorted["temperature_c"], df_sorted["margin_c"])],
            textposition="auto",
            textfont=dict(family=MONO_FONT_FAMILY, size=11, color="#ffffff"),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Current: %{x:.1f} °C<br>"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=threshold_warning,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text="Warn",
        annotation_position="top",
        annotation_font=dict(color="#f59e0b", size=10),
    )
    fig.add_vline(
        x=threshold_critical,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Crit",
        annotation_position="top",
        annotation_font=dict(color="#ef4444", size=10),
    )

    fig.update_layout(
        title=dict(
            text="<b>Component Temperature Ranking & Thermal Headroom</b>",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
        ),
        xaxis=dict(title="Temperature (°C)", range=[0, 110]),
        yaxis=dict(title="", tickfont=dict(size=11)),
        showlegend=False,
    )

    return _apply_dark_theme(fig, height=height)


# -----------------------------------------------------------------------------
# 5. Temperature Distribution Histogram (Enclosure Thermal Spread)
# -----------------------------------------------------------------------------
def create_temperature_distribution_chart(
    temp_grid: np.ndarray,
    threshold_warning: float = 78.0,
    threshold_critical: float = 85.0,
    height: int = 340,
) -> go.Figure:
    """
    Renders histogram distribution of spatial temperatures across the chassis mesh.
    """
    temps_flat = temp_grid.flatten()

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x=temps_flat,
            nbinsx=35,
            marker=dict(
                color="#0284c7",
                line=dict(color="#38bdf8", width=1),
            ),
            hovertemplate="Temp Bin: %{x:.1f} °C<br>Grid Elements: %{y}<extra></extra>",
            name="Mesh Element Count",
        )
    )

    fig.add_vline(
        x=threshold_warning,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text="Warning (78°C)",
        annotation_position="top right",
    )
    fig.add_vline(
        x=threshold_critical,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Critical (85°C)",
        annotation_position="top right",
    )

    fig.update_layout(
        title=dict(
            text="<b>Spatial Temperature Distribution Across Enclosure Mesh</b>",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
        ),
        xaxis=dict(title="Temperature (°C)"),
        yaxis=dict(title="Grid Cell Count"),
        showlegend=False,
    )

    return _apply_dark_theme(fig, height=height)


# -----------------------------------------------------------------------------
# 6. Cooling System Performance Trend (RPM vs Airflow vs Dissipation)
# -----------------------------------------------------------------------------
def create_cooling_performance_chart(telemetry_df: pd.DataFrame, height: int = 360) -> go.Figure:
    """
    Renders dual-axis cooling performance chart: Fan RPM vs Heat Dissipation vs Air Temp Rise (ΔT).
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Fan RPM trace (Primary Y)
    fig.add_trace(
        go.Scatter(
            x=telemetry_df["timestamp"],
            y=telemetry_df["fan_1_rpm"],
            name="Fan Array 1 RPM",
            line=dict(color="#06b6d4", width=2),
            hovertemplate="Fan 1: %{y:.0f} RPM<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=telemetry_df["timestamp"],
            y=telemetry_df["fan_2_rpm"],
            name="Fan Array 2 RPM",
            line=dict(color="#3b82f6", width=2, dash="dash"),
            hovertemplate="Fan 2: %{y:.0f} RPM<extra></extra>",
        ),
        secondary_y=False,
    )

    # Temperature delta & Dissipated heat (Secondary Y)
    fig.add_trace(
        go.Scatter(
            x=telemetry_df["timestamp"],
            y=telemetry_df["delta_t_inlet_outlet"],
            name="Airflow ΔT (Outlet - Inlet)",
            line=dict(color="#f97316", width=2.2),
            hovertemplate="Airflow ΔT: %{y:.1f} °C<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(
            text="<b>Cooling Subsystem Response: Fan RPM vs Airflow Temp Rise (ΔT)</b>",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
    )

    fig.update_xaxes(title="Timestamp")
    fig.update_yaxes(title="Fan Speed (RPM)", secondary_y=False, gridcolor=GRID_COLOR)
    fig.update_yaxes(title="Airflow ΔT (°C)", secondary_y=True, gridcolor="rgba(0,0,0,0)")

    return _apply_dark_theme(fig, height=height)


# -----------------------------------------------------------------------------
# 7. What-If Comparison Bar Chart (Baseline vs Simulated Conditions)
# -----------------------------------------------------------------------------
def create_what_if_comparison_chart(sim_df: pd.DataFrame, height: int = 380) -> go.Figure:
    """
    Renders side-by-side grouped bar chart comparing baseline vs what-if temperatures.
    """
    fig = go.Figure()

    # Baseline bars
    fig.add_trace(
        go.Bar(
            name="Baseline Nominal (25°C / 210W / 70% Fan)",
            x=sim_df["short_name"],
            y=sim_df["baseline_temp_c"],
            marker=dict(color="#475569"),
            text=[f"{v:.1f}°C" for v in sim_df["baseline_temp_c"]],
            textposition="auto",
            textfont=dict(family=MONO_FONT_FAMILY, size=10, color="#ffffff"),
            hovertemplate="Baseline: %{y:.1f} °C<extra></extra>",
        )
    )

    # Simulated bars
    sim_colors = []
    for d, s in zip(sim_df["delta_c"], sim_df["status"]):
        if s == "CRITICAL":
            sim_colors.append("#ef4444")
        elif s == "WARNING":
            sim_colors.append("#f59e0b")
        elif d < 0:
            sim_colors.append("#10b981")  # Cooler than baseline
        else:
            sim_colors.append("#0284c7")

    fig.add_trace(
        go.Bar(
            name="What-If Modified Condition",
            x=sim_df["short_name"],
            y=sim_df["simulated_temp_c"],
            marker=dict(color=sim_colors),
            text=[f"{v:.1f}°C ({d:+.1f})" for v, d in zip(sim_df["simulated_temp_c"], sim_df["delta_c"])],
            textposition="auto",
            textfont=dict(family=MONO_FONT_FAMILY, size=10, color="#ffffff"),
            hovertemplate="What-If: %{y:.1f} °C (Δ %{text})<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>What-If Scenario vs Baseline Operating Condition Comparison</b>",
            font=dict(family=CHART_FONT_FAMILY, size=14, color=TEXT_COLOR),
            x=0.02,
        ),
        barmode="group",
        xaxis=dict(title=""),
        yaxis=dict(title="Component Temperature (°C)", range=[0, 115]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
    )

    return _apply_dark_theme(fig, height=height)

