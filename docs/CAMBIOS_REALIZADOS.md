# Changelog

## Codebase Refactoring & Documentation

### Python Module Standardization
- `src/agente.py`: Implemented comprehensive Google-style docstrings, refined inline comments for clarity, and established a professional technical tone.
- `src/config.py`: Centralized configuration logic with detailed docstrings, ensuring clear property definitions and robust error handling documentation.
- `src/servidor.py`: Updated module headers and endpoint docstrings to reflect REST API standards.
- `src/dashboard.py`: Structured visualization logic with clear modular documentation.

---

## Persistence and Data Analysis

### SQLite Integration
- Transitioned from volatile, memory-based metric storage to persistent SQLite architecture (`data/metricas.db`).
- Introduced historical data retention, surviving system reboots.
- Deployed a new API endpoint, `/historial/{id}`, to facilitate time-series queries.

### Expanded Metric Collection
- **Disk Utilization:** Integrated logic to capture the usage percentage of the primary partition (`C:` or `/`).
- **Database Schema Migration:** Implemented automated schema upgrades, allowing the server to dynamically append the `disk` column to legacy databases.
- **Historical Charting:** Enhanced the Dashboard to render dynamic time-series line charts for CPU utilization over time via the `pandas` library.

---

## Automation and Tooling

### System Initialization Automation
- **`setup.bat`:** Created a comprehensive bootstrap script that automates environment preparation:
  - Validates Python installations.
  - Provisions the virtual environment (`venv`).
  - Resolves dependencies via `pip`.
  - Compiles necessary executable artifacts (Portable and Service variants).

---

## Enhanced Architecture Documentation

### `/docs` Overhaul
- **`instalacion.md`:** Standardized deployment instructions for both automated and source-based environments.
- **`COMPONENTES.md`:** Detailed system architecture, component responsibilities, and configuration structures.
- **`arquitectura.md`:** Refined the data flow diagrams and protocol definitions for advanced technical review.
- **`COMPARTIR_PROYECTO.md`:** Established clear protocols for system distribution and agent deployment scenarios.
- **`REFERENCIA_RAPIDA.md`:** Consolidated a technical cheat sheet for rapid operational reference.

---

## Remote Management and Security

### Remote Execution Capabilities
- **Reboot Operations:** Implemented administrative controls within the Dashboard to queue remote reboot commands.
- **Command Polling:** Enhanced the API to manage instruction queues, delivering commands to agents during standard metric payload exchanges.
- **Agent Integration:** `agente.py` successfully parses reboot instructions and executes OS-level `shutdown` protocols.

### Network and Reliability Enhancements
- **SSL/TLS Infrastructure:** Added configuration scaffolding for certificate-based HTTPS communication.
- **SMTP Alerts:** Built foundational integration for email-based node failure notifications.
- **Heartbeat Monitoring:** Integrated logic to flag agents that fail to transmit telemetry within a 5-minute threshold.

### Deferred Items
- Validating and enabling the SMTP configuration within `config.json` for production environments.

---

**Last Update:** January 2026
