"""
=============================================================================
Digital Twin & Real-Time Thermal Management Dashboard
Frontend Application Entry Point
=============================================================================
"""

import os
from pathlib import Path
import streamlit as st

# Configure Streamlit page settings - MUST be first Streamlit call
st.set_page_config(
    page_title="Digital Twin Thermal Management",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import components and data modules
from components.sidebar import render_sidebar
from data.simulated_data import generate_historical_telemetry

# Import dashboard pages
from dashboard.overview import render_overview_page
from dashboard.thermal_visualization import render_thermal_visualization_page
from dashboard.live_monitoring import render_live_monitoring_page
from dashboard.hotspot_detection import render_hotspot_detection_page
from dashboard.cooling_analytics import render_cooling_analytics_page
from dashboard.what_if_simulation import render_what_if_simulation_page


def load_custom_css():
    """Loads external CSS styling from assets/style.css."""
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found at assets/style.css")


def initialize_session_state():
    """Initializes global session state variables for telemetry and twin simulation."""
    if "telemetry_history" not in st.session_state:
        st.session_state["telemetry_history"] = generate_historical_telemetry(n_points=60)

    if "twin_synced" not in st.session_state:
        st.session_state["twin_synced"] = True

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "System Overview"


def main():
    """Main application lifecycle controller."""
    # 1. Inject custom industrial styling
    load_custom_css()

    # 2. Setup persistent telemetry session state
    initialize_session_state()

    # 3. Render sidebar navigation & digital twin status indicator
    selected_page = render_sidebar()

    # 4. Route to designated page controller
    if selected_page == "System Overview":
        render_overview_page()
    elif selected_page == "Thermal Visualization":
        render_thermal_visualization_page()
    elif selected_page == "Live Monitoring":
        render_live_monitoring_page()
    elif selected_page == "Hotspot Detection":
        render_hotspot_detection_page()
    elif selected_page == "Cooling Analytics":
        render_cooling_analytics_page()
    elif selected_page == "What-If Simulation":
        render_what_if_simulation_page()
    else:
        st.error(f"Page '{selected_page}' not found.")


if __name__ == "__main__":
    main()

