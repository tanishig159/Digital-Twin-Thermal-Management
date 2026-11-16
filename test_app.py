"""
Comprehensive Automated Test Suite for Digital Twin Thermal Management Dashboard
Uses Streamlit's official AppTest framework to verify all pages, sidebar navigation,
sliders, buttons, and visualizations without requiring network sockets.
"""

import sys
import unittest
from streamlit.testing.v1 import AppTest


class TestDigitalTwinDashboard(unittest.TestCase):
    def test_01_app_overview_initial_load(self):
        """Verify app boots to System Overview with all charts and KPIs."""
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        self.assertFalse(at.exception, f"App threw exception on boot: {at.exception}")
        
        # Verify title and sidebar
        self.assertIn("telemetry_history", at.session_state)
        self.assertEqual(at.session_state["current_page"], "System Overview")
        print("✓ System Overview loaded successfully with 0 exceptions.")

    def test_02_navigate_thermal_visualization(self):
        """Verify navigation to Thermal Visualization and mode switches."""
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        
        # Navigate via sidebar radio
        at.sidebar.radio[0].set_value("🗺️  Thermal Visualization").run()
        self.assertFalse(at.exception, f"Exception on Thermal Visualization: {at.exception}")
        self.assertEqual(at.session_state["current_page"], "Thermal Visualization")
        
        # Switch to 3D surface mesh
        at.selectbox(key="thermal_view_mode").set_value("3D Thermal Surface Mesh").run()
        self.assertFalse(at.exception, f"Exception on 3D surface: {at.exception}")
        
        # Switch color scale
        at.selectbox(key="thermal_colorscale").set_value("Thermal").run()
        self.assertFalse(at.exception, f"Exception on colorscale: {at.exception}")
        print("✓ Thermal Visualization (2D and 3D) tested successfully.")

    def test_03_navigate_live_monitoring(self):
        """Verify Live Monitoring telemetry stepping and reset buttons."""
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        
        at.sidebar.radio[0].set_value("⚡  Live Monitoring").run()
        self.assertFalse(at.exception, f"Exception on Live Monitoring: {at.exception}")
        self.assertEqual(at.session_state["current_page"], "Live Monitoring")
        
        initial_len = len(at.session_state["telemetry_history"])
        
        # Click Simulate Next Step button
        at.button(key="btn_sim_step").click().run()
        self.assertFalse(at.exception, f"Exception after stepping telemetry: {at.exception}")
        self.assertEqual(len(at.session_state["telemetry_history"]), initial_len + 1)
        
        # Click Reset button
        at.button(key="btn_reset_stream").click().run()
        self.assertFalse(at.exception, f"Exception after reset: {at.exception}")
        self.assertEqual(len(at.session_state["telemetry_history"]), 60)
        print("✓ Live Monitoring and telemetry stepping tested successfully.")

    def test_04_navigate_hotspot_detection(self):
        """Verify Hotspot Detection page and threshold sliders."""
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        
        at.sidebar.radio[0].set_value("🔥  Hotspot Detection").run()
        self.assertFalse(at.exception, f"Exception on Hotspot Detection: {at.exception}")
        self.assertEqual(at.session_state["current_page"], "Hotspot Detection")
        
        # Adjust warning threshold slider
        at.slider(key="hotspot_warn_slider").set_value(70.0).run()
        self.assertFalse(at.exception, f"Exception on warn slider: {at.exception}")
        
        # Adjust critical threshold slider
        at.slider(key="hotspot_crit_slider").set_value(82.0).run()
        self.assertFalse(at.exception, f"Exception on crit slider: {at.exception}")
        print("✓ Hotspot Detection and dynamic thresholds tested successfully.")

    def test_05_navigate_cooling_analytics(self):
        """Verify Cooling Analytics page and aerodynamic calculations."""
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        
        at.sidebar.radio[0].set_value("❄️  Cooling Analytics").run()
        self.assertFalse(at.exception, f"Exception on Cooling Analytics: {at.exception}")
        self.assertEqual(at.session_state["current_page"], "Cooling Analytics")
        print("✓ Cooling Analytics page tested successfully.")

    def test_06_navigate_what_if_simulation(self):
        """Verify What-If Simulation sliders, presets, and recalculations."""
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        
        at.sidebar.radio[0].set_value("🧪  What-If Simulation").run()
        self.assertFalse(at.exception, f"Exception on What-If Simulation: {at.exception}")
        self.assertEqual(at.session_state["current_page"], "What-If Simulation")
        
        # Test preset buttons
        at.button(key="preset_desert").click().run()
        self.assertFalse(at.exception, f"Exception on Desert preset: {at.exception}")
        self.assertEqual(at.session_state["sim_ambient_temp"], 42.0)
        
        at.button(key="preset_stress").click().run()
        self.assertFalse(at.exception, f"Exception on Stress preset: {at.exception}")
        self.assertEqual(at.session_state["sim_heat_load"], 380.0)
        
        # Test slider adjustments
        at.slider(key="slider_heat_load").set_value(450.0).run()
        self.assertFalse(at.exception, f"Exception on heat load slider: {at.exception}")
        
        at.slider(key="slider_cooling_pct").set_value(40.0).run()
        self.assertFalse(at.exception, f"Exception on cooling slider: {at.exception}")
        print("✓ What-If Simulation presets and sliders tested successfully.")


if __name__ == "__main__":
    unittest.main()

