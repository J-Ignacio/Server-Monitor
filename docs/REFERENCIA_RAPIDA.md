# Quick Reference Guide

## Core Execution

### Central Server Initialization
```powershell
# Double-click or execute:
.\Iniciar_NOC.bat
```
*Initializes both the FastAPI service and the Streamlit Dashboard simultaneously.*

### Remote Agent Initialization
```powershell
# Double-click or execute:
.\AGENTE_PORTABLE.exe
```
*Initializes metric collection and transmission. Requires prior IP configuration in `config.json`.*

---

## Critical Endpoints

| Resource | URL | Description |
|----------|-----|-------------|
| **Dashboard** | `http://localhost:8501` | Primary visualization interface. |
| **API State** | `http://localhost:8000/estado` | GET endpoint returning the current node array (JSON). |
| **API Docs** | `http://localhost:8000/docs` | Swagger UI detailing REST endpoints. |

---

## Data Structures

**GET `/estado` Response Format:**
```json
{
  "SERVER01 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 42.0,
    "disk": 55.4
  },
  "SERVER02 (192.168.1.101)": {
    "cpu": 28.5,
    "ram": 41.3,
    "temp": 38.5,
    "disk": 80.1
  }
}
```

---

## Configuration Parameter Override

To manually override the Central Server routing on an agent node, edit the generated `config/config.json`:

```json
{
  "servidor_central": {
    "ip": "192.168.4.143",
    "puerto": 8000
  }
}
```

---

## Common Diagnostic Resolutions

| Symptom | Probable Cause | Corrective Action |
|---------|----------------|-------------------|
| Empty Dashboard | Agents unable to establish connection. | Validate `servidor_central` IP in agent `config.json`. |
| "Port 8000 in use" | Ghost API process occupying binding. | Terminate `python.exe` processes or reboot Central Server. |
| Connection Timeout | Ingress traffic dropped by OS firewall. | Execute firewall `allow` rule for TCP port 8000. |

---

## Developer Bootstrap Workflow

```powershell
# 1. Initialize Python Environment
python -m venv venv
.\venv\Scripts\activate

# 2. Resolve Dependencies
pip install -r requirements.txt

# 3. Generate Artifacts
.\herramientas.bat
```
