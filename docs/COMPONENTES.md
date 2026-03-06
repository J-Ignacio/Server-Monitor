# Technical Components and Executables

## Executables

### `Iniciar_NOC.bat` (Central Server)
**Automated launch script for the central monitoring system.**

Functionality:
1. Initializes the FastAPI service on port 8000.
2. Implements a 3-second delay for service readiness.
3. Launches the Streamlit Dashboard.

Usage:
```powershell
# Execute via double-click or command line
.\Iniciar_NOC.bat
```

---

### `NOC_SERVICIO.exe` (Remote Agent)
**Compiled service executable for remote monitoring.**

Generated utilizing PyInstaller from `src/agente_servicio.py`. Deployed via `instalar_agente.bat`.

Usage:
```powershell
# Execute installing script as Administrator
.\instalar_agente.bat
```

**To regenerate the executable:**
```powershell
# Execute compilation tool
.\herramientas.bat
# Select Option [1]
```

---

## Source Code Components

### 1. Remote Agent (`src/agente.py`)
**Deployed on remote servers (via `AGENTE_FINAL.exe` or source).**

Core Responsibilities:
- Gathers CPU, RAM, and Disk (Primary Partition) metrics at 5-second intervals.
- Transmits JSON payloads to the Central Server.
- Implements automated retry logic for transient network failures.
- **Remote Management:** Processes reboot commands dispatched by the Central Server.
- **Hardware Sensors:** Interfaces with WMI/Open Hardware Monitor to retrieve thermal metrics.

Configuration Parsing:
- **Dynamic IP Detection:** Automatically resolves its local IP address upon initialization.
- **Central Routing:** Reads `SERVIDOR_CENTRAL_IP` from `src/config.py` (or `config.json`).

Output Example:
```
[Info] Agent started successfully: SERVER01 (192.168.1.100)
[Info] Reporting endpoint: http://192.168.1.100:8000/reportar
[Success] Data transmitted - CPU: 45.2% | RAM: 62.1% | Disk: 55.4%
```

---

### 2. Central API Server (`src/servidor.py`)
**FastAPI service hosted on the NOC infrastructure.**

REST Endpoints:
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/estado` | Retrieves the latest metrics array for all registered nodes. |
| GET | `/historial/{id}` | Retrieves the historical timeseries data (last 50 data points). |
| POST | `/reportar` | Ingestion endpoint for remote agent payloads. |
| POST | `/admin/reiniciar/{id}` | Queues a reboot instruction for a specific agent node. |

**GET /estado - Response Structure:**
```json
{
  "SERVER01 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "disk": 55.4,
    "temp": 42.0
  }
}
```

**POST /reportar - Payload Structure:**
```json
{
  "id_servidor": "SERVER01 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1,
  "temp": 42.0,
  "disk": 55.4
}
```

Default Port: `8000`

---

### 3. Monitoring Dashboard (`src/dashboard.py`)
**Streamlit-based visualization interface.**

Features:
- Dynamically renders node cards for all registered servers.
- Utilizes progress bars for resource utilization visualization.
- **Historical Analysis:** Line charts plotting CPU utilization over time.
- **Administrative Controls:** Integrated reboot mechanism with a confirmation modal.
- Configured for asynchronous updates every 2 seconds.

Default Port: `8501`

---

## Communication Architecture

```text
[REMOTE NODE]             [CENTRAL SERVER]           [WEB CLIENT]
   Agent                      FastAPI                  Dashboard
  .exe/.py                  servidor.py               dashboard.py
      |                          |                         |
      |--- POST /reportar ------>|                         |
      |    (5s interval)         |                         |
      |                    Persists to DB                  |
      |                          |                         |
      |                          |<----- GET /estado ------|
      |                          |                         |
      |                          |------- JSON ----------->|
      |<--- 200 OK Response -----|      (2s interval)      |
```

---

## Global Configuration Parameters

Parameters are centralized in `config/config.json`.

### Agent Configuration
- `intervalo_envio`: Frequency of metric transmission (Default: 5s).
- `timeout`: Network request timeout threshold.

### Server Configuration
- `ip`: Central server IPv4 address binding.
- `puerto`: API listening port (Default: 8000).

### Security/System Configuration
- `usar_ssl`: Toggles HTTPS protocol enforcement.
- `logs_habilitados`: Enables rotating file log generation.
