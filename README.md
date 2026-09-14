# 🪰 Fruit Fly Football (Drosophila Connectome 3D Soccer Simulation)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black.svg)](https://threejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c.svg)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/Tests-12%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

An interactive 3D WebGL multi-agent soccer simulation combined with a biological **Drosophila melanogaster (Fruit Fly)** Spiking Neural Network (SNN) visual-motor circuit.

Watch 10 autonomous fruit flies compete in a fast-paced **5v5 football match (Team Red vs Team Blue)** inside a sunny 3D arena with full aerodynamic wing flapping, realistic soccer ball physics, tactical positioning, and real-time fly neural/biometric telemetry.

---

## 🌟 Key Features

### ⚽ 1. 3D WebGL Football Arena (5v5)
- **10 Autonomous Insects**: 5v5 squad match featuring **Team Red** vs **Team Blue**.
- **Procedural Fly Anatomy**: Segmented compound eyes, bristle micro-geometry, faceted chitin thorax/abdomen, and dynamic high-frequency wing oscillation pivots.
- **Physical Soccer Ball Engine**: Dynamic 3D ball simulation with restitution, ground rolling friction, aerodynamic drag, crossbar rebounds, and net collisions.
- **Sunny Stadium Environment**: Lush green textured turf with authentic pitch markings, corner flags, outside goal nets, 4 floodlight towers, LED advertising boards, and surrounding grassland with trees.
- **Live Scoreboard & Match Events**: Tracks Team Red vs Team Blue score, match time, shot speed, kickoff resets, and post-goal celebration maneuvers.

### 🧠 2. Fly Tactical AI & Role Dynamics
- **Goalkeepers (GK)**: Lateral patrol along the goal line, defensive D-area shot interception, and diving saves anchored to the goalmouth.
- **Defenders (DEF1, DEF2)**: Dynamic zone coverage, flanking passes, and tracking incoming attackers.
- **Midfielders (MID)**: Pitch transitions, loose-ball recovery, and central playmaking.
- **Strikers (ST)**: High-speed pursuit, diving strikes, and offensive pressure on the opposing goal.

### 📊 3. Real-Time Neural & Biometric Telemetry HUD
- **Interactive Fly Selection**: Click any fly in 3D or select from the roster bar at the bottom to focus monitoring.
- **Live Biometrics**:
  - **Nervous / Arousal Level (%)**: Dynamically rises when near the ball or in goal danger zones, triggering adrenaline surge states.
  - **Wingbeat Frequency**: High-frequency aerodynamic rate (up to 135+ Hz).
  - **Spike Count**: Neural spike frequency within the sensory-motor loop (/50ms).
  - **Stamina Gauge**: Depletes during high-speed sprint dives, regenerates during zone positioning.
  - **Optic Flow Angle**: Real-time directional visual vector.
  - **SNN Oscilloscope Waveform**: Canvas-based real-time membrane potential wave.
- **Minimizable Telemetry Card**: Toggle button collapses the telemetry card into a sleek status pill to enjoy unobstructed views of the pitch.

### 🎥 4. Broadcast Camera Modes
- **Broadcast TV (Default)**: Cinematic camera smoothly tracking match play.
- **Fly POV**: First-person insect compound eye view chasing the ball.
- **Ball Cam**: Dynamic tracking camera centered on the soccer ball.
- **Top-Down**: Overhead tactical perspective of pitch formations.

### 🧬 5. Drosophila SNN Connectome Engine (Python)
- **Leaky Integrate-and-Fire (LIF)**: 2,000-neuron vectorized PyTorch spiking neural network.
- **Circuit Architecture**:
  - **Sensory Layer (T4/T5)**: 300 optic lobe direction-selective neurons.
  - **Central Complex (CX)**: 1,400 recurrent neurons modeling sensorimotor integration.
  - **Descending Neurons (DN)**: 300 motor output neurons (steering turn, escape jump, roll/dive).
- **Adaptive Thresholds**: Dynamic homeostatic membrane thresholds with absolute refractory periods.
- **Connectome Integration**: FlyWire / FAFB / NeuPrint API support with biological weight distributions.

---

## 📁 Repository Structure

```
fruit-fly/
├── web/                           # 3D WebGL Client (HTML5 / Three.js)
│   ├── index.html                 # Stadium viewport, HUD overlays, and roster
│   ├── app.js                     # 3D scene, physics engine, tactical AI, biometrics
│   ├── styles.css                 # Glassmorphism cyber-HUD styling
│   └── assets/                    # Static assets & 3D model drop zone
├── src/                           # Python Biological SNN & Server Engine
│   ├── brain_sim.py               # Vectorized LIF Drosophila SNN simulation
│   ├── data_engine.py             # Connectome loader & NeuPrint/FlyWire API bridge
│   ├── game_interface.py          # Visual motion & Poisson optic flow processor
│   └── server_3d.py               # Built-in lightweight HTTP & SSE server
├── tests/                         # Automated test suite (12 tests)
│   ├── test_brain_sim.py          # SNN dynamics, decay, refractory tests
│   ├── test_data_engine.py        # Connectome structure & weight matrix tests
│   ├── test_game_interface.py     # Motion processing & action controller tests
│   ├── test_pipeline_integration.py # End-to-end closed loop tests
│   └── test_server_3d.py          # HTTP server & asset delivery tests
├── data/                          # Pre-generated connectome graph files
├── scripts/
│   └── verify_env.py              # Environment verification tool
├── main.py                        # Simulation launcher & SNN diagnostic CLI
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules
└── README.md                      # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or later
- Any modern web browser with WebGL support (Chrome, Edge, Firefox, Safari)

### 1. Run the 3D Football Simulation

You can launch the simulation immediately with **zero configuration**:

```bash
python main.py
```

This will automatically start the local server and open your browser at **`http://localhost:8080`**.

> **Alternative (Direct HTTP Server)**:
> ```bash
> python -m http.server 8080 --directory web
> ```
> Then open [http://localhost:8080](http://localhost:8080) in your browser.

---

### 2. (Optional) Full Environment Setup for SNN Diagnostics

To run the biological connectome spiking neural network and test suite:

```bash
# Clone repository
git clone https://github.com/your-username/fruit-fly.git
cd fruit-fly

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Run Biological SNN Telemetry Diagnostics

To view the real-time Spiking Neural Network firing rates and descending motor decisions in your terminal:

```bash
python main.py --diagnostics
```

CLI options:
- `--steps <N>`: Number of simulation timesteps to run.
- `--device <cpu|cuda>`: Hardware acceleration device.
- `--gui`: Display OpenCV neural raster plot and visual receptive field HUD.

---

## 🧪 Running Tests

All core mechanics are thoroughly verified with unit and integration tests:

```bash
pytest tests/ -v
```

Expected output:
```text
tests/test_brain_sim.py::test_subthreshold_decay PASSED                  [  8%]
tests/test_brain_sim.py::test_spike_generation_and_reset PASSED          [ 16%]
tests/test_brain_sim.py::test_refractory_period PASSED                   [ 25%]
tests/test_brain_sim.py::test_directional_sensory_to_motor_pathways PASSED [ 33%]
tests/test_data_engine.py::test_synthetic_connectome_structure PASSED    [ 41%]
tests/test_data_engine.py::test_weight_matrix_properties PASSED          [ 50%]
tests/test_data_engine.py::test_connectome_serialization PASSED          [ 58%]
tests/test_game_interface.py::test_screen_grabber PASSED                 [ 66%]
tests/test_game_interface.py::test_visual_motion_processor PASSED        [ 75%]
tests/test_game_interface.py::test_game_action_controller_cooldown PASSED [ 83%]
tests/test_pipeline_integration.py::test_closed_loop_pipeline_dry_run PASSED [ 91%]
tests/test_server_3d.py::test_server_3d_startup_and_static_files PASSED  [100%]

============================= 12 passed in 17.46s =============================
```

---

## 🎮 Controls & Interaction

| Control | Description |
| :--- | :--- |
| **Mouse Drag / Left Click** | Orbit & rotate the 3D stadium camera |
| **Right Click + Drag** | Pan stadium view |
| **Mouse Scroll** | Zoom in / out |
| **Click on Any Fly** | Inspect and lock neural telemetry on that player |
| **Roster Bar (Bottom)** | Select specific Team Red or Team Blue flies |
| **Broadcast Buttons** | Switch between TV, Fly POV, Ball Cam, and Top-Down |
| **Reset Ball Button** | Place ball back on center mark for fresh kickoff |
| **Minimize Button (`_`)** | Collapse/expand neural biometrics card |

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
