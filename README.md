# NOC Monitoring System

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-00a393.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A centralized, real-time telemetry and monitoring system designed for Network Operations Centers (NOC). This architecture enables continuous tracking of CPU, RAM, Disk utilization, and hardware temperatures across multiple distributed servers within a local area network (LAN) or virtual private network (VPN).

## 🚀 System Architecture Overview

The system operates on a client-server model consisting of three primary components:

1. **Remote Agent (`agente.py` / `AGENTE_FINAL.exe`):** A lightweight daemon deployed on target servers. It autonomously polls hardware sensors and transmits JSON payloads to the central server.
2. **Central API Server (`servidor.py`):** A high-performance REST API built with FastAPI. It ingests agent telemetry, validates payloads, and persists time-series data into a SQLite database.
3. **Monitoring Dashboard (`dashboard.py`):** A dynamic, asynchronous Streamlit interface that queries the Central API to render real-time visualizations and historical charts.

---

## ⚡ Quick Start

### Initial Environment Setup (Central Server)

To initialize the development environment and compile the necessary executables, execute the provided bootstrap script:

```bat
:: Double-click the following script to create the virtual environment,
:: install dependencies, and compile the PyInstaller artifacts.
.\setup.bat
```

### Launching the NOC Application

**Automated Launch (Recommended):**
```bat
:: Double-click to concurrently start the FastAPI server and the Streamlit Dashboard.
.\Iniciar_NOC.bat
```

**Manual Execution (Development):**
```powershell
# Ensure the virtual environment is active
.\venv\Scripts\activate

# Terminal 1: Initialize the FastAPI service
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# Terminal 2: Initialize the Streamlit Dashboard
streamlit run src/dashboard.py
```

### Deploying the Remote Agent

1. Generate the standalone executables utilizing `herramientas.bat` (Option 1).
2. Navigate to the `dist/` directory and transfer `AGENTE_PORTABLE.exe` and `instalar_agente.bat` to the target remote server.
3. Execute `instalar_agente.bat` with **Administrator privileges** on the remote server.
4. Update `config/config.json` on the remote server to specify the IP address of the Central Server.
5. Relaunch the agent.

---

## 📁 Repository Structure

| Resource | Description |
|----------|-------------|
| **`setup.bat`** | Environment initialization and dependency resolution script. |
| **`limpiar.bat`** | Environment teardown script (removes `venv` and temporary build artifacts). |
| **`Iniciar_NOC.bat`** | Unified launch script for the API and Dashboard services. |
| `src/agente.py` | Source code for the remote telemetry agent. |
| `src/servidor.py` | Source code for the FastAPI central server. |
| `src/dashboard.py` | Source code for the Streamlit visualization interface. |
| `config/config.json` | Centralized configuration file (generated automatically). |
| `test_configuracion.py` | Diagnostic script for validating environment configuration. |
| `logs/` | Directory containing rotating application logs. |

---

## 📚 Technical Documentation

Comprehensive documentation detailing deployment strategies, system architecture, and configuration parameters is available in the `/docs` directory:

- [Deployment Guide](./docs/instalacion.md)
- [System Architecture & Data Flow](./docs/arquitectura.md)
- [Component Specifications](./docs/COMPONENTES.md)
- [Distribution Protocols](./docs/COMPARTIR_PROYECTO.md)
- [Quick Reference Cheat Sheet](./docs/REFERENCIA_RAPIDA.md)
- [Changelog](./docs/CAMBIOS_REALIZADOS.md)

---

## ⚙️ System Requirements

- **Runtime:** Python 3.8 or higher.
- **Network:** Port 8000 TCP must be accessible on the Central Server.
- **Connectivity:** Reliable network routing between the Remote Agents and the Central Server.
- **Hardware Metrics (Windows):** For accurate thermal polling on Windows environments, [OpenHardwareMonitor](https://openhardwaremonitor.org/) must be executed with Administrator privileges.
