# Installation Guide

## Central Server (NOC Node)

### Option A: Automated Execution (Recommended)

1. **Extract the project archive** to a dedicated directory.
2. **Execute `Iniciar_NOC.bat`**
   - Initializes the FastAPI service on port 8000.
   - Automatically launches the Streamlit Dashboard.
3. **Access the Dashboard:** Navigate to `http://localhost:8501` in your web browser.

### Option B: Manual Execution (Development Environment)

```powershell
# 1. Prepare the Python environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Terminal 1: Initialize the API
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# 3. Terminal 2: Initialize the Dashboard
streamlit run src/dashboard.py
```

### Firewall Configuration (Initial Setup)

**Windows (PowerShell as Administrator):**
```powershell
netsh advfirewall firewall add rule name="NOC Monitor" dir=in action=allow protocol=tcp localport=8000
```

---

## Remote Agent

### Option A: Compiled Executable (Recommended)

1. **Access the remote server** via RDP:
   ```cmd
   mstsc /v:<SERVER_IP>
   ```

2. **Deploy the Executable:** Copy `AGENTE_PORTABLE.exe` to a designated directory (e.g., `C:\Monitor\`).

3. **Initialize the Agent:** Execute `AGENTE_PORTABLE.exe`.
   - The application will automatically generate the `config/` directory.
   - If connection fails initially, terminate the process.
   - Modify `config/config.json` to specify the correct Central Server IP.
   - Relaunch `AGENTE_PORTABLE.exe`.

### Option B: Python Source Execution

1. **Deploy Source:** Copy `src/agente.py` to the remote server.

2. **Install Dependencies:**
   ```powershell
   pip install requests psutil wmi
   ```

3. **Configure Central IP:** Edit `agente.py` (Line 8) or configure via `config/config.json`:
   ```python
   IP_CENTRAL = "192.168.4.143"  # Replace with the Central Server IP
   ```

4. **Execute:**
   ```powershell
   python agente.py
   ```

---

## System Verification

- **Dashboard:** Confirm nodes populate at `http://localhost:8501`
- **API Health:** Verify JSON response at `http://localhost:8000/estado`
- **Agent Logs:** Confirm console output indicates "Data transmitted"

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Dashboard fails to open | Verify `http://localhost:8501` is accessible in the browser. |
| "Port 8000 in use" error | Reassign the port in configuration or terminate the conflicting process. |
| Agent reports "Connection error" | Verify `IP_CENTRAL` is accurate and the firewall permits traffic on port 8000. |
| Access denied on `.bat` execution | Execute the batch script with Administrator privileges. |

## Enabling Temperature Metrics (Windows)

If the dashboard displays "Temperature: N/A", the Windows WMI interface is not broadcasting sensor data natively.

**Resolution:**
1. Download and extract [OpenHardwareMonitor](https://openhardwaremonitor.org/).
2. Execute `OpenHardwareMonitor.exe` as **Administrator**.
3. Navigate to **Options** and enable:
   - "Run on Windows Startup"
   - "Minimize to Tray"
4. Maintain the application in a minimized state; the agent will automatically poll the exposed WMI metrics.
