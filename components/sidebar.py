"""
Digital Twin Thermal Management - Sidebar Navigation & Status Component
Renders the navigation menu, digital twin synchronization indicator,
chassis specifications, and simulation controls.
"""

from typing import Tuple
import streamlit as st


PAGES = [
    "System Overview",
    "Thermal Visualization",
    "Live Monitoring",
    "Hotspot Detection",
    "Cooling Analytics",
    "What-If Simulation",
]

PAGE_ICONS = {
    "System Overview": "📊",
    "Thermal Visualization": "🗺️",
    "Live Monitoring": "⚡",
    "Hotspot Detection": "🔥",
    "Cooling Analytics": "❄️",
    "What-If Simulation": "🧪",
}


def render_sidebar() -> str:
    """
    Renders sidebar navigation, digital twin status indicator, and telemetry controls.
    Returns the currently selected page name.
    """
    with st.sidebar:
        # Brand & Header
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0;">
                <div style="display:flex; align-items:center; gap: 0.5rem;">
                    <span style="font-size: 1.6rem;">🔬</span>
                    <div>
                        <div style="font-size: 1.05rem; font-weight: 800; letter-spacing: -0.02em; color: #f8fafc; line-height:1.2;">
                            DIGITAL TWIN
                        </div>
                        <div style="font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; color: #38bdf8; text-transform: uppercase;">
                            Thermal Management
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Digital Twin Status Card
        twin_synced = st.session_state.get("twin_synced", True)
        status_dot = "status-dot" if twin_synced else "status-dot warning"
        status_label = "TWIN SYNCHRONIZED" if twin_synced else "TELEMETRY PAUSED"

        st.markdown(
            f"""
            <div style="background: rgba(17, 24, 39, 0.85); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 8px; padding: 0.75rem; margin-bottom: 1.25rem;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 0.4rem;">
                    <div style="display:flex; align-items:center; gap: 0.5rem;">
                        <span class="{status_dot}"></span>
                        <span style="font-size: 0.72rem; font-weight: 700; color: #34d399; letter-spacing: 0.05em;">{status_label}</span>
                    </div>
                    <span style="font-family:'JetBrains Mono',monospace; font-size: 0.68rem; color: #64748b;">18ms</span>
                </div>
                <div style="font-size: 0.7rem; color: #94a3b8; line-height: 1.4;">
                    <div>Target: <strong style="color:#cbd5e1;">ET-402 Enclosure</strong></div>
                    <div>Mesh Fidelity: <strong style="color:#38bdf8;">High (75×50)</strong></div>
                    <div>Source: <span style="color:#a78bfa; font-weight:600;">SIMULATED TELEMETRY</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation Menu
        st.markdown(
            "<div style='font-size: 0.7rem; font-weight: 700; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem;'>Dashboard Navigation</div>",
            unsafe_allow_html=True,
        )

        # Format navigation options with icons
        nav_options = [f"{PAGE_ICONS[p]}  {p}" for p in PAGES]

        # Determine index from session state
        current_page = st.session_state.get("current_page", PAGES[0])
        default_index = 0
        if current_page in PAGES:
            default_index = PAGES.index(current_page)

        selected_nav = st.radio(
            label="Navigate",
            options=nav_options,
            index=default_index,
            label_visibility="collapsed",
            key="sidebar_nav_radio",
        )

        # Parse selected page string
        selected_page = selected_nav.split("  ", 1)[1]
        st.session_state["current_page"] = selected_page

        st.markdown("<hr style='margin: 1.2rem 0; border-color: rgba(148, 163, 184, 0.1);'>", unsafe_allow_html=True)

        # Enclosure Spec Brief
        st.markdown(
            """
            <div style="font-size: 0.7rem; font-weight: 700; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem;">
                Enclosure Hardware Spec
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.08); border-radius: 6px; padding: 0.65rem; font-size: 0.72rem; color: #94a3b8; line-height: 1.6;">
                <div style="display:flex; justify-content:space-between;"><span>Chassis Form:</span> <span style="color:#cbd5e1; font-weight:600;">300 × 200 mm</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Thermal Zones:</span> <span style="color:#cbd5e1; font-weight:600;">6 Active Nodes</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Cooling Type:</span> <span style="color:#cbd5e1; font-weight:600;">Forced Dual-Fan PWM</span></div>
                <div style="display:flex; justify-content:space-between;"><span>Max Heat Cap:</span> <span style="color:#cbd5e1; font-weight:600;">500 W Peak</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='margin: 1.2rem 0; border-color: rgba(148, 163, 184, 0.1);'>", unsafe_allow_html=True)

        # Phase Notice & Footer
        st.markdown(
            """
            <div style="padding: 0.5rem 0; font-size: 0.68rem; color: #64748b; line-height: 1.4;">
                <div style="color: #38bdf8; font-weight: 600; margin-bottom: 2px;">Phase 1: Frontend Dashboard</div>
                <div>Simulated telemetry mode. Staged for ANSYS FEA, Reduced-Order ROMs, and Physical IoT stream integration.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return selected_page

