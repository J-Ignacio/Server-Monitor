# Deployment and Distribution Guide

This document outlines the standard procedures for distributing the monitoring application across various environments, ensuring stable deployment configurations.

## Scenario A: Agent Deployment (Monitoring Remote Nodes)
*Follow this procedure to deploy the tracking agent to target machines without transferring the entire repository.*

### 1. Configure the Central Target
1. Access the Central Server and open `config/config.json`.
2. Locate the `servidor_central` block.
3. Update the `ip` field to reflect the fixed IP address of your Central Server (e.g., `"ip": "192.168.1.50"`).

### 2. Compile the Agent Executable
1. Execute `herramientas.bat` on the Central Server.
2. Select option **[1] Compile Agents**.
3. Await the completion of the PyInstaller build process. The output will be located in the `dist/` directory.

### 3. Distribute to Target Nodes
1. Navigate to the `dist/` directory.
2. Transfer the executable (`NOC_SERVICIO.exe`) and the installation script (`instalar_agente.bat`) to the target node.
3. On the target node, execute `instalar_agente.bat` with **Administrator privileges**.
4. The agent will initialize as a background service and commence metric transmission.

*Note: If updating an existing agent deployment, you must delete the legacy `config/config.json` on the target machine to force it to adopt the newly compiled IP routing.*

---

## Scenario B: Full System Migration (Development/NOC Setup)
*Follow this procedure to migrate the entire codebase, including the API and Dashboard, to a new administrative machine.*

### 1. Codebase Transfer
1. Compress the project directory.
   - **Crucial:** Exclude the following directories to prevent environment corruption and reduce payload size:
     - `venv/` (Python virtual environment)
     - `build/` (Compilation artifacts)
     - `dist/` (Compiled executables)
     - `__pycache__/` (Python bytecode cache)
     - `.git/` (Version control history)
2. Transfer the compressed archive to the new Central Server.

### 2. Environment Initialization
1. Extract the archive.
2. Execute `setup.bat`. This script will:
   - Detect or install Python.
   - Generate a fresh virtual environment (`venv`).
   - Install required dependencies from `requirements.txt`.
   - Compile the local executables.

### 3. Service Initialization
1. Execute `Iniciar_NOC.bat` to launch the API and Dashboard services.

---

## Troubleshooting Connectivity

### 1. Agent Reports Legacy IP
**Symptom:** The agent continues attempting connections to an outdated Central Server IP.
**Resolution:**
1. Terminate the agent process.
2. Locate the `config/` directory adjacent to the executable.
3. Delete the `config.json` file.
4. Relaunch the agent to regenerate the configuration based on the compiled defaults.

### 2. Connection Timeout / Refusal
**Symptom:** Agent logs indicate a timeout; the Central Server is unreachable.
**Resolution:**
The Windows Firewall on the Central Server is likely restricting inbound traffic on the designated port.
1. Open PowerShell as Administrator on the Central Server.
2. Execute the firewall configuration command:
   ```powershell
   New-NetFirewallRule -DisplayName "NOC Monitor" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
   ```

### 3. Destination Host Unreachable
**Symptom:** Network partition between the Agent and Central Server (e.g., disparate subnets).
**Resolution:**
Ensure proper routing exists between the nodes. Implement a VPN solution (e.g., Tailscale or WireGuard) to establish a flattened overlay network if physical routing is unavailable.
