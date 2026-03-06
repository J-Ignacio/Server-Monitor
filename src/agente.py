"""
Remote Monitoring Agent Module.

This module acts as an agent running on remote servers. It collects system metrics
such as CPU usage, RAM utilization, temperature, and disk usage at a predefined
interval. The collected metrics are then transmitted to the centralized monitoring
server.

Dependencies:
    - psutil: For collecting system metrics.
    - requests: For sending data to the centralized server.
    - wmi (Optional): For advanced temperature reading on Windows systems.
"""

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

try:
    import wmi
    import pythoncom
except ImportError:
    wmi = None
    pythoncom = None

try:
    from config import (
        URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT,
        AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO, VERIFICAR_SSL,
        LOGS_HABILITADOS, BASE_DIR, AGENTE_IP_MANUAL,
        SERVIDOR_CENTRAL_IP, SERVIDOR_CENTRAL_PUERTO
    )
except Exception as e:
    print(f"\n[FATAL ERROR] Failed to load configuration: {e}")
    print("Potential cause: Insufficient permissions to read or create 'config.json' in 'config' directory.")
    input("Press ENTER to exit...")
    sys.exit(1)

def configurar_logger() -> None:
    """
    Configures the application logger.

    Sets up a stream handler to print logs to the console. If file logging is enabled
    in the configuration, it additionally configures a rotating file handler that maintains
    up to 3 backup files, each up to 1MB in size.
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if LOGS_HABILITADOS:
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "agente.log"
        
        handlers.append(
            RotatingFileHandler(
                str(log_file),
                maxBytes=1_000_000,
                backupCount=3,
                encoding='utf-8'
            )
        )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )

def obtener_ip_real() -> str:
    """
    Detects the primary IP address of the local server.

    If a manual IP address is configured, it returns that value immediately.
    Otherwise, it attempts to connect to the central server to determine the primary
    routing IP. It also scans all available network interfaces, filtering out loopback
    and auto-configuration (APIPA) addresses, returning a concatenated string if multiple
    valid addresses are discovered.

    Returns:
        str: The detected IP address or addresses of the server. Defaults to '127.0.0.1'.
    """
    if AGENTE_IP_MANUAL:
        return AGENTE_IP_MANUAL

    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((SERVIDOR_CENTRAL_IP, SERVIDOR_CENTRAL_PUERTO))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass

    try:
        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == socket.AF_INET:
                    ip = snic.address
                    if not ip.startswith("127.") and not ip.startswith("169.254."):
                        ips.add(ip)
    except Exception:
        pass

    if not ips:
        return '127.0.0.1'

    return " - ".join(sorted(list(ips)))

def obtener_temperatura() -> float:
    """
    Retrieves the system CPU temperature.

    Attempts multiple strategies for fetching the temperature:
        1. WMI interface via OpenHardwareMonitor/LibreHardwareMonitor.
        2. Standard WMI (MSAcpi_ThermalZoneTemperature).
        3. Cross-platform `psutil` sensors (primarily for Linux).

    Returns:
        float: The detected temperature in degrees Celsius, or 0.0 if not found.
    """
    if wmi:
        namespaces = ["root\\OpenHardwareMonitor", "root\\LibreHardwareMonitor"]
        for ns in namespaces:
            try:
                ohm = wmi.WMI(namespace=ns)
                sensors = ohm.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == 'Temperature':
                        nombre = sensor.Name.upper()
                        if any(x in nombre for x in ['CPU', 'CORE', 'PACKAGE', 'TCTL', 'TDIE']):
                            return float(sensor.Value)
            except Exception:
                continue

        try:
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                kelvin = temps[0].CurrentTemperature
                celsius = (kelvin - 2732) / 10.0
                if celsius > 0:
                    return celsius
        except Exception:
            pass

    try:
        temps = psutil.sensors_temperatures()
        if temps:
            return next(iter(temps.values()))[0].current
    except Exception:
        pass
    
    return 0.0

def ejecutar_diagnostico() -> None:
    """
    Executes an initial system diagnostic to check hardware sensors and network state.

    Prints diagnostic information to standard output, verifying WMI capabilities,
    detected temperature sensors, and available network interfaces.
    """
    print("\n[DIAGNOSTIC] --- SENSOR DIAGNOSTIC ---")
    if not wmi:
        print("[Warning] 'wmi' library not detected.")
        return

    namespaces = ["root\\OpenHardwareMonitor", "root\\LibreHardwareMonitor"]
    encontrado = False

    for ns in namespaces:
        try:
            ohm = wmi.WMI(namespace=ns)
            sensores = ohm.Sensor()
            if sensores:
                print(f"[Success] Connected to namespace {ns}.")
                encontrado = True
                temps = [s for s in sensores if s.SensorType == 'Temperature']
                if temps:
                    print("  Detected temperature sensors:")
                    for s in temps:
                        print(f"  - Name: '{s.Name}' | Value: {s.Value}°C")
                else:
                    print("  [Warning] Connected, but no temperature sensors found.")
        except Exception:
            pass
    
    if not encontrado:
        print("[Warning] Open/Libre Hardware Monitor instances not detected.")
        print("  Ensure the software is running with Administrator privileges.")

    print("\n[DIAGNOSTIC] --- NETWORK DIAGNOSTIC ---")
    try:
        try:
            print(f"  - Primary IP (Hostname): {socket.gethostbyname(socket.gethostname())}")
        except Exception:
            pass

        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == socket.AF_INET:
                    print(f"  - {interface}: {snic.address}")
    except Exception:
        pass
    print("-----------------------------------\n")

def enviar_datos(stop_event=None) -> None:
    """
    Continuously collects and transmits system metrics to the centralized server.

    Manages system diagnostics, initializes necessary components like COM for WMI,
    and handles retries using defined configurations if network communication fails.
    It can be terminated gracefully via the provided threading Event.

    Args:
        stop_event (threading.Event, optional): Event flag to trigger shutdown loop.
    """
    configurar_logger()

    if wmi and pythoncom:
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
    
    hostname = socket.gethostname().strip()
    ip_real = obtener_ip_real().strip()
    ID_SERVIDOR = f"{hostname} ({ip_real})"

    if not VERIFICAR_SSL:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print(f"[Info] Agent started successfully: {ID_SERVIDOR}")
    print(f"[Info] Reporting endpoint: {URL_REPORTAR}")
    print(f"[Info] Interval configured: {AGENTE_INTERVALO}s")
    print(f"[Info] Temperature Support: {'ACTIVE (WMI)' if wmi else 'INACTIVE (WMI library missing)'}")

    logging.info(f"Agent initiated: {ID_SERVIDOR}")
    logging.info(f"Reporting URL: {URL_REPORTAR}")
    logging.info(f"Interval: {AGENTE_INTERVALO}s | Temp Support: {'WMI' if wmi else 'Native'}")

    ejecutar_diagnostico()

    intentos_fallidos = 0
    
    while True:
        if stop_event and stop_event.is_set():
            break

        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "temp": obtener_temperatura(),
                "disk": psutil.disk_usage(os.path.abspath(os.sep)).percent
            }
            
            response = requests.post(
                URL_REPORTAR,
                json=metricas,
                timeout=AGENTE_TIMEOUT,
                verify=VERIFICAR_SSL
            )
            response.raise_for_status()
            
            respuesta_json = response.json()
            if respuesta_json.get("comando") == "reiniciar":
                print("[Alert] REBOOT COMMAND RECEIVED: Rebooting server in 5 seconds...")
                logging.warning("[Alert] REBOOT COMMAND RECEIVED: Rebooting server in 5 seconds...")
                time.sleep(5)
                if os.name == 'nt':
                    os.system("shutdown /r /t 0 /f")
                else:
                    os.system("shutdown -r now")

            print(f"[Success] Data transmitted - CPU: {metricas['cpu']:.1f}% | RAM: {metricas['ram']:.1f}% | Disk: {metricas['disk']:.1f}%")
            logging.info(f"Transmitted - CPU: {metricas['cpu']}% | RAM: {metricas['ram']}% | Disk: {metricas['disk']}% | Temp: {metricas['temp']:.1f}°C")
            intentos_fallidos = 0

        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            intentos_fallidos += 1
            msg_error = f"Connection error (Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}): {e}"
            
            if isinstance(e, requests.exceptions.ConnectTimeout):
                print(f"[Warning] Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Server timeout.")
                msg_error = "Timeout: The central server is unresponsive."
            elif isinstance(e, requests.exceptions.ConnectionError):
                print(f"[Warning] Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Connection failure. Is the server online?")
            elif isinstance(e, requests.exceptions.HTTPError):
                 print(f"[Warning] Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: HTTP Server error ({e.response.status_code}).")
            else:
                print(f"[Warning] Attempt {intentos_fallidos}/{AGENTE_REINTENTOS}: Network anomaly: {e}")
                msg_error = "Connection rejected."
            
            logging.warning(msg_error)

            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"[Error] Max retries exceeded. Pausing for {AGENTE_ESPERA_REINTENTO}s...")
                logging.error(f"Retry threshold breached. Pausing operations for {AGENTE_ESPERA_REINTENTO}s...")
                time.sleep(AGENTE_ESPERA_REINTENTO)
                intentos_fallidos = 0
        except Exception as e:
            print(f"[Error] Unexpected exception: {e}")
            logging.exception(f"Unexpected exception encountered: {e}")
            
        if stop_event:
            if stop_event.wait(AGENTE_INTERVALO):
                break
        else:
            time.sleep(AGENTE_INTERVALO)

if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Agent halted unexpectedly: {e}")
        logging.critical(f"Agent termination due to critical exception: {e}")
        input("Press ENTER to exit...")
