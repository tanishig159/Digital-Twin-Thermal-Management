# Digital Twin & Real-Time Thermal Management Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-1.46.1-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-6.2.0-3F4F75?style=for-the-badge&logo=Plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.3.3-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-2.2.6-013243?style=for-the-badge&logo=NumPy&logoColor=white)](https://numpy.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Status](https://img.shields.io/badge/Status-Phase%201%20Frontend%20Active-10b981?style=for-the-badge)]()

An industrial-grade digital twin frontend dashboard for real-time thermal telemetry, spatial 2D/3D heat field visualization, automated hotspot detection, cooling subsystem analytics, and interactive "What-If" parametric scenario simulation.

---

## 📌 Project Overview & Scope

> **Important Scope Note (Phase 1):**
> This phase implements the **Frontend Dashboard & Interactive Visualizations ONLY**.
> All thermal fields, sensor streams, and operational states use **realistic simulated data** generated via physical first-order thermal lag and multi-source 2D Gaussian convective drift models.
> The codebase is built with a strictly modular architecture to seamlessly dock with **ANSYS Fluent/Icepak, FEA solvers, ML surrogate ROMs, and physical IoT edge telemetry** in future phases.

---

## 💻 Technology Stack

- **Python 3.10+**: Core programming language.
- **Streamlit**: Web application framework and reactive state management.
- **Plotly (Graph Objects & Express)**: High-performance interactive engineering visualizations (2D contour heatmaps, 3D surface meshes, dual-axis waveforms).
- **Pandas**: Time-series telemetry buffering, windowing, and dataframe operations.
- **NumPy**: Multi-source Gaussian diffusion modeling, spatial mesh grid calculations, and stochastic thermal noise injection.

---

## 🏗️ Project Architecture

```
Digital-Twin-Thermal-Management/
│
├── app.py                      # Application entry point & page router
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive documentation
├── test_app.py                 # Automated unit test suite (AppTest)
│
├── dashboard/                  # Dedicated page controllers
│   ├── overview.py             # System Overview & KPI command center
│   ├── thermal_visualization.py# 2D Heatmap & 3D Surface mesh visualizer
│   ├── live_monitoring.py      # Real-time sensor telemetry & rolling trends
│   ├── hotspot_detection.py    # Hotspot auditor & dynamic thresholding
│   ├── cooling_analytics.py    # Aerodynamic & cooling COP analytics
│   └── what_if_simulation.py   # Parametric What-If scenario simulator
│
├── components/                 # Reusable UI & visualization components
│   ├── sidebar.py              # Navigation menu & digital twin status card
│   ├── kpi_cards.py            # Industrial KPI cards, badges, & alerts
│   └── charts.py               # Dark-theme Plotly engineering visualizations
│
├── data/                       # Telemetry & physical simulation engine
│   └── simulated_data.py       # Spatial 2D mesh, lag equations, & what-if engine
│
├── assets/                     # UI styling & design assets
│   └── style.css               # Industrial dark theme design system
│
└── .streamlit/
    └── config.toml             # Streamlit server & dark theme configuration
```

---

## 🎨 Industrial UI/UX Design System

The dashboard is engineered with a **modern industrial control room aesthetic**:
- **Background Palette**: Deep charcoal / dark navy (`#0a0f1d`, `#111827`, `#141e33`) with subtle glassmorphic backdrop glow.
- **Accent Hierarchy**: Cyan (`#06b6d4`), Sky Blue (`#38bdf8`), Emerald (`#10b981`), Amber (`#f59e0b`), Crimson (`#ef4444`), Purple (`#a78bfa`).
- **Typography**: Clean hierarchy powered by *Plus Jakarta Sans* for headings/labels and *JetBrains Mono* for telemetry readings and coordinates.
- **Pulsing Status Dots**: Animated digital twin synchronization indicator with millisecond latency metrics.
- **Dynamic Gradient Heatmaps**: High-contrast engineering thermal scales (`Turbo`, `Thermal`, `Jet`, `Inferno`) depicting physical heat dissipation.

---

## 🖥️ Key Dashboard Features & Pages

### 1. System Overview
- **5 High-Impact KPI Cards**: Maximum Temperature, Average Temperature, Ambient (Inlet) Temperature, Active Hotspots Count, and Cooling Subsystem Status.
- **Multi-Component Trend Chart**: Past 60-minute historical telemetry with Warning (78°C) and Critical (90°C) threshold reference lines.
- **Component Headroom Ranking**: Horizontal bar chart comparing all 6 thermal nodes and operating margins.
- **Enclosure Subsystem Telemetry**: Real-time heat dissipation (W), airflow (CFM), mass flow rate (kg/s), and thermal resistance ($R_{th}$).
- **Real-Time Thermal Alerts Log**: Color-coded severity events with actionable recommendations.

### 2. Thermal Visualization
- **Electronic Enclosure Form Factor**: Real physical dimensions (300 × 200 mm chassis) representing an industrial electronics unit.
- **2D Contour Heatmap**: Smooth multi-source convective thermal diffusion from cool air intake (left) to heated exhaust (right).
- **Component Annotations**: Interactive bounding boxes and labels for CPU/SoC, VRM Stage, Li-Ion Battery, Motor Inverter, DDR5 Memory, and HF Transformer.
- **Interactive Controls**:
  - Color palette switcher (`Turbo`, `Thermal`, `Jet`, `Plasma`, `Inferno`).
  - Toggle isotherm contour lines.
  - Toggle component bounding outlines.
  - Configurable hotspot highlight slider.
  - **3D Thermal Elevation Surface View** for topographical thermal mesh inspection.
- **Localized Component Inspector**: Inspect individual zone coordinates, footprint, power dissipation, and thermal safety margins.

### 3. Live Monitoring
- **Real-Time Node Telemetry**: Dedicated sensor monitoring for CPU, Power Module (VRM), Battery Pack, Motor Controller, and Ambient sensor.
- **Interactive Stream Controls**:
  - `Simulate Next Reading Step`: Push new dynamic telemetry frames with physical first-order thermal inertia.
  - `Reset Stream History`: Reinitialize baseline telemetry buffer.
  - Noise / fluctuation selector (`Low`, `Standard`, `Dynamic Stress`).
- **Rolling Multi-Channel Waveforms**: Filter visible telemetry channels interactively.
- **Raw Telemetry Frame Buffer**: Inspect recent sliding-window telemetry packets.

### 4. Hotspot Detection
- **Dynamic User Sliders**:
  - Advisory Warning Threshold (60°C – 90°C).
  - Emergency Critical Threshold (75°C – 105°C).
- **Automatic Zone Classification**: Re-evaluates all components in real time (Normal, Warning, Critical).
- **Headroom Ranking & Mesh Histogram**: Spatial distribution histogram of temperatures across all grid cells.
- **Mitigation Guidance**: Zone-by-zone remediation advice table.

### 5. Cooling Analytics
- **Cooling Status & Effectiveness**: Dual-fan PWM monitoring (Fan 1 & Fan 2 RPM), total CFM, and coefficient of performance (COP).
- **Thermodynamic Balance**: Inlet temp, outlet temp, temperature rise ($\Delta T = T_{out} - T_{in}$), and air-absorbed thermal wattage.
- **Fan RPM vs $\Delta T$ Performance Waveform**: Dual-axis trend analysis.
- **Prescriptive Cooling Recommendations**: Actionable advice prioritized by urgency (High, Medium, Low).

### 6. What-If Simulation
- **Interactive Boundary Condition Sliders**:
  - Heat Load ($50\,\text{W} - 500\,\text{W}$)
  - Ambient Temperature ($15^\circ\text{C} - 45^\circ\text{C}$)
  - Cooling Intensity ($10\% - 100\%$)
  - Convection Coefficient $h$ ($5 - 150\,\text{W/m}^2\text{K}$)
- **Quick Engineering Presets**:
  - 🟢 Nominal Baseline
  - 🏜️ Desert / High Ambient
  - ⚡ Max Workload Stress
  - ⚠️ Cooling Fan Degradation
- **Instant Demonstration Computation**: Re-computes predicted component temperatures, system safety status, and modulated 2D thermal field.
- **Side-by-Side Baseline Comparison**: Grouped bar chart comparing nominal vs simulated temperatures with $\Delta T$ delta indicators.

---

## 🚀 Installation & Launch Instructions

### Prerequisites
- Python 3.10+ (tested with Python 3.12)
- pip

### 1. Clone & Navigate
```bash
git clone <YOUR_REPOSITORY_URL>
cd Digital-Twin-Thermal-Management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit Dashboard
```bash
streamlit run app.py
```

The application will launch in your default web browser at:
`http://localhost:8501`

### 4. Run the Automated Test Suite
```bash
python test_app.py
```

---

## 🔮 Future Development Roadmap

- **Phase 2 - High-Fidelity Physics Solver**: Docking ANSYS Fluent / Icepak via PyFluent / PyAEDT for high-resolution 3D CFD thermal simulations.
- **Phase 3 - ML Surrogate Modeling**: Training physics-informed neural networks (PINN) or Reduced-Order Models (ROMs) to deliver sub-millisecond inference for real-time digital twins.
- **Phase 4 - Physical Edge Telemetry**: Ingestion of live thermocouple and PT100 RTD sensor streams via MQTT, OPC-UA, and Modbus TCP.
