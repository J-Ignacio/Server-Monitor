# Architecture and Data Flow

## System Flow Diagram

```text
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│   REMOTE NODE    │         │  CENTRAL SERVER  │         │    WEB CLIENT    │
│     (Agent)      │         │    (FastAPI)     │         │   (Dashboard)    │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         │ POST /reportar             │                            │
         │ {cpu, ram, disk, temp}     │                            │
         ├───────────────────────────>│                            │
         │                            │                            │
         │                  Persists to DB (SQLite)                │
         │                            │                            │
         │                            │<───── GET /estado ─────────│
         │                            │                            │
         │                            ├────── JSON Response ──────>│
         │                            │       (Updates 2s)         │
         │ (5s Interval)              │                            │
         ├───────────────────────────>│                            │
```

## System Components

### 1. Remote Agent (`agente.py`)
- Deployed on target infrastructure nodes.
- **Metric Collection:** Captures CPU, RAM, Disk utilization, and Temperature at defined intervals.
- **Transmission:** Dispatches JSON payloads to the `/reportar` POST endpoint.
- **Resilience:** Implements exponential backoff and retry mechanisms for network partitions.
- **Sensors:** Interrogates WMI/psutil for thermal data, contingent on hardware support and administrative privileges.

### 2. Central Server (`servidor.py`)
- Hosts a FastAPI REST interface on the centralized NOC hardware.
- **Endpoints:**
  - `POST /reportar`: Ingests and validates metric payloads via Pydantic schemas.
  - `GET /estado`: Returns the most recently recorded metrics for active nodes.
  - `GET /historial/{id}`: Returns a time-series array of historical metrics.
- **Storage Layer:** Utilizes SQLite (`data/metricas.db`) for lightweight, persistent data retention.
- **Network:** Binds to port `8000` by default.

### 3. Monitoring Dashboard (`dashboard.py`)
- Streamlit application serving as the primary visualization layer.
- Implements asynchronous polling to refresh node states dynamically.
- Renders responsive UI components, historical charts, and administrative controls.

## Communication Protocol

### Inbound Request (Agent → Server)
```http
POST /reportar HTTP/1.1
Host: 192.168.4.143:8000
Content-Type: application/json

{
  "id_servidor": "SERVER01 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1,
  "temp": 42.0,
  "disk": 55.4
}
```

### Server Response (Server → Agent)
```json
{
  "status": "ok"
}
```

### Data Query (Dashboard → Server)
```http
GET /estado HTTP/1.1
Host: localhost:8000
```

### Query Response (Server → Dashboard)
```json
{
  "SERVER01 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 42.0,
    "disk": 55.4,
    "timestamp": "2023-10-27T10:00:00Z"
  }
}
```

## Security Considerations

- **Authentication:** Currently operates without native authentication; relies on network perimeter security (VLAN/VPN).
- **Transport:** Defaults to plain HTTP. Production deployments over un-trusted networks require enabling the SSL/TLS configuration parameter.
- **Future Enhancements:** Token-based authentication and strict origin validation should be implemented prior to wide-scale deployment.

## System Limitations

- **Thermal Metrics:** Dependency on OS-level APIs (WMI/psutil) or external services (OpenHardwareMonitor) requires specific hardware configurations and elevated privileges.
- **Scalability:** The current SQLite implementation is optimized for environments scaling up to approximately 100 concurrent nodes. Environments exceeding this threshold may require migration to a robust RDBMS (e.g., PostgreSQL).
