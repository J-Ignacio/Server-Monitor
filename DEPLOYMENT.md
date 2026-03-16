# Deployment Guide: Fixed Local Server

This document outlines the analysis of the current NOC Monitoring System setup and the exact steps required to deploy it to a fixed, permanent local server.

## 1. Code Refactoring (Replacing `localhost` or `127.0.0.1`)

The current architecture correctly abstracts the IP configuration out of the Python scripts and into `config/config.json`. **No code changes are required** to the `.py` files themselves to change the IP.

To deploy to a fixed server (e.g., with IP `192.168.1.50`):
1.  Open `config/config.json` on the **Central Server**.
2.  Update the `ip` value under `servidor_central`:
    ```json
    "servidor_central": {
        "ip": "192.168.1.50",
        "puerto": 8000,
        "host": "0.0.0.0"
    }
    ```
3.  Keep `"host": "0.0.0.0"`. This allows the API to listen on all available network interfaces.
4.  Ensure that the **Agent** machines receive this updated `config.json` so they know the exact IP of the new fixed server.

*Optional Dynamic Environment Approach:* If you strictly prefer environment variables, `src/config.py` can be updated to pull `SERVIDOR_CENTRAL_IP` from `os.environ`. However, relying on the existing JSON configuration is already highly robust.

## 2. Existing System Fixes & Network Blocks

A thorough review of `src/servidor.py`, `src/dashboard.py`, `src/agente.py`, and `src/config.py` shows:

*   **API Server (`src/servidor.py`):** Runs using `host=SERVIDOR_CENTRAL_HOST` (which is `"0.0.0.0"`). This is perfectly set up for a dedicated server as it listens to incoming requests from the LAN, not just localhost.
*   **Dashboard (`src/dashboard.py`):** Explicitly connects to the API via `127.0.0.1`. Since both the Dashboard and the API will run on the *same* fixed central server, this is completely safe and avoids network latency or IP-change issues.
*   **Agent (`src/agente.py`):** Transmits to `URL_REPORTAR` using the `SERVIDOR_CENTRAL_IP`. As long as the JSON config points to the fixed server's IP, the agent will find the server.
*   **Conclusion:** There are no hardcoded network blocks preventing deployment.

## 3. Deployment Automation (Service Creation)

To ensure the system stays active 24/7 and restarts automatically on boot, you must configure it as a service.

### For Linux (systemd)
Create two separate service files.

1.  **API Service (`/etc/systemd/system/noc-api.service`):**
    ```ini
    [Unit]
    Description=NOC Monitor API (FastAPI)
    After=network.target

    [Service]
    User=your_user
    WorkingDirectory=/path/to/your/repo
    ExecStart=/path/to/your/repo/venv/bin/python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    ```

2.  **Dashboard Service (`/etc/systemd/system/noc-dashboard.service`):**
    ```ini
    [Unit]
    Description=NOC Monitor Dashboard (Streamlit)
    After=network.target noc-api.service

    [Service]
    User=your_user
    WorkingDirectory=/path/to/your/repo
    ExecStart=/path/to/your/repo/venv/bin/streamlit run src/dashboard.py
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    ```

**Enable and start the services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable noc-api noc-dashboard
sudo systemctl start noc-api noc-dashboard
```

### For Windows (NSSM)
If the fixed server is running Windows:

1.  Download [NSSM (Non-Sucking Service Manager)](http://nssm.cc/).
2.  Open an Administrator Command Prompt.
3.  Install the **API Service**:
    ```cmd
    nssm install NOC_API
    ```
    *   **Path:** `C:\path\to\repo\venv\Scripts\python.exe`
    *   **Arguments:** `-m uvicorn src.servidor:app --host 0.0.0.0 --port 8000`
    *   **Directory:** `C:\path\to\repo`
4.  Install the **Dashboard Service**:
    ```cmd
    nssm install NOC_Dashboard
    ```
    *   **Path:** `C:\path\to\repo\venv\Scripts\streamlit.exe`
    *   **Arguments:** `run src/dashboard.py`
    *   **Directory:** `C:\path\to\repo`
5.  Start the services:
    ```cmd
    nssm start NOC_API
    nssm start NOC_Dashboard
    ```

## 4. Network Visibility (Firewall)

To allow other devices on the LAN to communicate with the fixed server, you must open specific ports.

*   **Port 8000:** Required for Agents to send telemetry to the API.
*   **Port 8501:** Required for administrators to view the Streamlit Dashboard from other machines.

### On Linux (UFW):
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 8501/tcp
sudo ufw reload
```

### On Windows (PowerShell as Administrator):
```powershell
New-NetFirewallRule -DisplayName "NOC API (8000)" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "NOC Dashboard (8501)" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
```

## 5. Dependency Lockdown

The current `requirements.txt` lists base packages (`fastapi`, `streamlit`, `psutil`, etc.) but does not pin versions. To ensure a completely identical environment on the new server:

1.  On the **current development machine** (where the system works perfectly), activate your virtual environment.
2.  Run the following command to generate a strict dependency file:
    ```bash
    pip freeze > requirements.txt
    ```
3.  Deploy this updated `requirements.txt` to the new fixed server. This prevents future updates to libraries from breaking the system.
