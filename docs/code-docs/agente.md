# Technical Documentation: Monitoring Agent

This document details the operation of the Monitoring Agent, including both the data collection logic (`agente.py`) and the wrapper to run it as a Windows Service (`agente_servicio.py`).

## 1. Full Source Code: Agent Logic (`src/agente.py`)
## 1. Agent Logic (`src/agente.py`)

### 1.1. Configuration and Logging
The agent starts by loading the configuration and establishing the logging system. It also detects the machine's real IP to identify itself correctly to the server.

```python
"""Remote agent: collects server metrics and sends them to the central server"""
import psutil
import requests
import time
import socket
import sys
import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import urllib3
# ... imports ...
from config import URL_REPORTAR, AGENTE_INTERVALO, ...

# Attempt to import WMI for temperature support on Windows
try:
    import wmi
    import pythoncom
except ImportError:
    wmi = None
    pythoncom = None

try:
    from config import URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT, AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO, VERIFICAR_SSL, LOGS_HABILITADOS, BASE_DIR
except Exception as e:
    print(f"\n[FATAL ERROR] Could not load configuration: {e}")
    print("Possible cause: Lack of permissions to create 'config.json' or 'config' folder.")
    input("Press ENTER to exit...")
    sys.exit(1)

# --- Logging Configuration ---
def configurar_logger():
    handlers = [logging.StreamHandler(sys.stdout)] # Always show in console
    
    if LOGS_HABILITADOS:
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "agente.log"
        
        # Rotates the file when it reaches 1MB, keeps up to 3 old copies
        handlers.append(RotatingFileHandler(str(log_file), maxBytes=1_000_000, backupCount=3, encoding='utf-8'))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )

# Detects the server's real IP on the local network
def obtener_ip_real():
    """Gets the local IP of the server"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
```

### 1.2. Temperature Sensors (WMI vs psutil)
This is the most complex logic of the agent. Windows does not expose CPU temperature natively and easily.

```python
def obtener_temperatura():
    """Attempts to get CPU temperature (Supports WMI/OHM)"""
    # 1. Windows Strategy: WMI
    # 1. Windows Strategy: WMI (OpenHardwareMonitor or MSAcpi)
    if wmi:
        try:
            # Option A: OpenHardwareMonitor / LibreHardwareMonitor
            # Namespaces: root\OpenHardwareMonitor, root\LibreHardwareMonitor
            ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor") # Tests both in loop
            sensors = ohm.Sensor()
            for sensor in sensors:
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    return float(sensor.Value)
        except:
            pass # OHM not available
            # Option A: OpenHardwareMonitor
            ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            # ... iterate sensors ...
        except: pass

        try:
            # Option B: Standard WMI (MSAcpi)
            # Returns tenths of Kelvin. (K - 273.2) = Celsius
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                # Conversion from tenths of Kelvin to Celsius
                # (K - 273.2)
                kelvin = temps[0].CurrentTemperature
                celsius = (kelvin - 2732) / 10.0
                if celsius > 0: return celsius
        except:
            pass
        except: pass

    # 2. General Strategy: psutil
    # 2. General Strategy: psutil (Linux/Mac)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Returns the first available temperature
            return next(iter(temps.values()))[0].current
    except:
        pass
        if temps: return next(iter(temps.values()))[0].current
    except: pass
    
    return 0.0
```

def ejecutar_diagnostico():
    """Prints to console which sensors are detected on startup"""
    print("\n🔍 --- SENSOR DIAGNOSTICS ---")
    # ... WMI and sensor detection logic ...
    print("-----------------------------------\n")
- **Priority:** WMI is prioritized over `psutil` on Windows.
- **Precision Math:** The calculation `(K - 2732) / 10.0` is fundamental since thermal sensors under the ACPI standard usually return values in $10^{-1}$ Kelvin.

### 1.3. Telemetry Loop and Resilience
The core of the agent. It captures data, sends it, and handles network errors without stopping.

```python
def enviar_datos(stop_event=None):
    """Collects metrics and sends them to the central server with retry logic."""
    configurar_logger()
    # ... COM and SSL initialization ...
    
    hostname = socket.gethostname().strip()
    ip_real = obtener_ip_real().strip()
    ID_SERVIDOR = f"{hostname} ({ip_real})"

    # Initialize COM for WMI (Vital for threads/services)
    if wmi and pythoncom:
        try:
            pythoncom.CoInitialize()
        except: pass

    # Silence SSL warnings if verification is disabled
    if not VERIFICAR_SSL:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print(f"✓ Agent started: {ID_SERVIDOR}")
    print(f"✓ Reporting to: {URL_REPORTAR}")
    print(f"⏱️  Send interval: {AGENTE_INTERVALO}s")
    print(f"🌡️  Temperature Support: {'ACTIVE (WMI)' if wmi else 'INACTIVE (wmi library not found)'}")
    logging.info(f"🚀 Agent started: {ID_SERVIDOR}")
    logging.info(f"📡 Reporting to: {URL_REPORTAR}")
    logging.info(f"⏱️  Interval: {AGENTE_INTERVALO}s | Temp: {'WMI' if wmi else 'Native'}")

    # Run visual diagnostic on startup
    ejecutar_diagnostico()

    intentos_fallidos = 0
    
    while True:
        if stop_event and stop_event.is_set():
            break
        if stop_event and stop_event.is_set(): break

        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "temp": obtener_temperatura(),
                "disk": psutil.disk_usage(os.path.abspath(os.sep)).percent
            }
            
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT, verify=VERIFICAR_SSL)
            response.raise_for_status()  # Throws an exception for HTTP error codes (4xx or 5xx)
            
            # Check if the server sent us a command in the response
            respuesta_json = response.json()
            if respuesta_json.get("comando") == "reiniciar":
                print(f"⚠️  COMMAND RECEIVED: Rebooting server in 5 seconds...")
                logging.warning(f"⚠️  COMMAND RECEIVED: Rebooting server in 5 seconds...")
                time.sleep(5)
                if os.name == 'nt': # Windows
                    os.system("shutdown /r /t 0 /f")
                else: # Linux / Others
                    os.system("shutdown -r now")

            print(f"✓ Data sent - CPU: {metricas['cpu']:.1f}% | RAM: {metricas['ram']:.1f}% | Disk: {metricas['disk']:.1f}%")
            logging.info(f"✓ Sent - CPU: {metricas['cpu']}% | RAM: {metricas['ram']}% | Disk: {metricas['disk']}% | Temp: {metricas['temp']:.1f}°C")
            intentos_fallidos = 0 # Reset counter on success

        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            intentos_fallidos += 1
            msg_error = f"Connection error ({intentos_fallidos}/{AGENTE_REINTENTOS}): {e}"
            
            if isinstance(e, requests.exceptions.ConnectTimeout):
                print(f"⚠️  Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Timeout. The server is not responding.")
                msg_error = "Timeout: The central server is not responding."
            elif isinstance(e, requests.exceptions.ConnectionError):
                print(f"⚠️  Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Connection error. Is the server on?")
            elif isinstance(e, requests.exceptions.HTTPError):
                 print(f"⚠️  Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Server error ({e.response.status_code}).")
            else:
                print(f"⚠️  Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Network error: {e}")
                msg_error = "Connection refused: Is the central server on?"
            
            logging.warning(f"⚠️ {msg_error}")

            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Maximum retries exceeded. Waiting {AGENTE_ESPERA_REINTENTO}s...")
                logging.error(f"✗ Retry limit reached. Pausing {AGENTE_ESPERA_REINTENTO}s...")
                time.sleep(AGENTE_ESPERA_REINTENTO)
                intentos_fallidos = 0 # Reset counter for next cycle
        except Exception as e:
            print(f"⚠️ An unexpected error occurred: {e}")
            logging.exception(f"⚠️ Unexpected error: {e}")
            
        if stop_event:
            if stop_event.wait(AGENTE_INTERVALO):
                break
        else:
            time.sleep(AGENTE_INTERVALO)

if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        print(f"\n[ERROR] The agent stopped: {e}")
        logging.critical(f"🛑 The agent stopped due to critical error: {e}")
        input("Press ENTER to exit...")
```

- Business Logic: Method 1 is prioritized over 2 because `MSAcpi` often reports static values if the BIOS manufacturer does not correctly expose thermal zones.

- Precision Math: The calculation `(K - 2732) / 10.0` is fundamental since thermal sensors under the ACPI standard usually return values in $10^{-1}$ Kelvin.

### 4. Telemetry and Network Resilience Loop

The core of the agent, in charge of data capture and HTTP communication management.

```python
def enviar_datos():
    """Infinite reporting loop with error state handling"""
    intentos_fallidos = 0
    
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),      # Blocks 1s for true average
                "ram": psutil.virtual_memory().percent,     # RAM usage % snapshot
                "temp": obtener_temperatura()               # Value calculated in the previous block
            }
            
            # Payload transmission via POST
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT)
            
            if response.status_code == 200:
                print(f"✓ Data sent successfully")
                intentos_fallidos = 0
            else:
                intentos_fallidos += 1
            # Remote Commands Management (Reboot)
            if response.json().get("comando") == "reiniciar":
                os.system("shutdown /r /t 0 /f")

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
            # Exponential backoff or wait logic
            intentos_fallidos += 1
            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Unreachable server. Waiting {AGENTE_ESPERA_REINTENTO}s...")
                intentos_fallidos = 0 # Reset counter to avoid overflow
                time.sleep(AGENTE_ESPERA_REINTENTO)
        except (requests.exceptions.ConnectionError, ...):
            # Exponential retry logic
            time.sleep(AGENTE_ESPERA_REINTENTO)
        
        time.sleep(AGENTE_INTERVALO)

```

- CPU Metric: `psutil.cpu_percent(interval=1)` is vital. If the interval were 0, the metric would be an instantaneous spike with no statistical value. One second allows averaging the cycles of the execution threads.
- **CPU Metric:** `psutil.cpu_percent(interval=1)` blocks execution for 1 second to calculate the actual average usage.
- **Network Management:** Specific exceptions are caught to prevent the agent from crashing due to micro-cuts.

- Network Management: Specific exceptions from `requests` are caught. This prevents the agent from collapsing due to internet micro-cuts or scheduled central server reboots.

### 5. Script Entry Point

Protection of the main execution flow.

### 1.4. Entry Point
```python
if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        # Catches any unhandled error to prevent sudden terminal closure
        print(f"\n[CRITICAL ERROR] The agent stopped: {e}")
        print(f"\n[ERROR] The agent stopped: {e}")
        input("Press ENTER to exit...")
```

### 6. Execution as a Windows Service
## 2. Windows Service (`src/agente_servicio.py`)

For production environments, the agent runs as a background service.

## 2. Full Source Code: Windows Service (`src/agente_servicio.py`)

This file acts as a "wrapper" that allows Windows to manage the Python script as a background service (without a window).

```python
"""
Wrapper to run the Agent as a Windows Service.
Requires Administrator privileges to install.
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import threading
from pathlib import Path

# Ensure we can import the 'agente' module from the same directory
if getattr(sys, 'frozen', False):
    # If it runs as .exe
    base_path = Path(sys.executable).parent
else:
    # If it runs as .py script
    base_path = Path(__file__).resolve().parent

sys.path.append(str(base_path))

from agente import enviar_datos


class AgenteService(win32serviceutil.ServiceFramework):
    _svc_name_ = "NOCMonitorAgente"
    _svc_display_name_ = "NOC Monitor Agent"
    _svc_description_ = "Sends CPU/RAM/Disk metrics to the central NOC server."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_event = threading.Event()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop_event.set()

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )

        try:
            enviar_datos(stop_event=self.stop_event)
        except Exception as e:
            servicemanager.LogErrorMsg(f"Fatal error in agent: {e}")


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AgenteService)
```

### Technical Explanation
- **Wrapper (`agente_servicio.py`):** Uses the `pywin32` library to interact with the Windows Service Control Manager (SCM).
- **Stop Signal:** The service sends a threading event (`stop_event`) to the `enviar_datos()` function to allow a clean shutdown without killing the process abruptly.
- **Installation:** Managed via the `instalar_agente.bat` script, which registers the service with automatic startup.
```

- Purpose: The block `if __name__ == "__main__":` prevents the agent from starting to collect data if the file is accidentally imported by another script. The final `input()` is a courtesy for Windows users, allowing them to read the error before the console window disappears