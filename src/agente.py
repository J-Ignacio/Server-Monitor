"""Agente remoto: recopila métricas del servidor y las envía a la central"""
import psutil
import requests
import time
import socket
import sys
import os
from pathlib import Path
import urllib3

# Intento de importar WMI para soporte de temperatura en Windows
try:
    import wmi
except ImportError:
    wmi = None

try:
    from config import URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT, AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO, VERIFICAR_SSL
except Exception as e:
    print(f"\n[ERROR FATAL] No se pudo cargar la configuración: {e}")
    print("Posible causa: Falta de permisos para crear 'config.json' o carpeta 'config'.")
    input("Presione ENTER para salir...")
    sys.exit(1)

# Detecta la IP real del servidor en la red local
def obtener_ip_real():
    """Obtiene la IP local del servidor"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Identificador único del servidor (nombre + IP)
hostname = socket.gethostname().strip()
ip_real = obtener_ip_real().strip()
ID_SERVIDOR = f"{hostname} ({ip_real})"

# Silenciar advertencias de SSL si la verificación está desactivada
if not VERIFICAR_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(f"✓ Agente iniciado: {ID_SERVIDOR}")
print(f"✓ Reportando a: {URL_REPORTAR}")
print(f"⏱️  Intervalo de envío: {AGENTE_INTERVALO}s")
print(f"🌡️  Soporte Temperatura: {'ACTIVO (WMI)' if wmi else 'INACTIVO (Librería wmi no encontrada)'}")

def obtener_temperatura():
    """Intenta obtener la temperatura de la CPU (Soporta WMI/OHM)"""
    # 1. Estrategia Windows: WMI
    if wmi:
        try:
            # Opción A: OpenHardwareMonitor (Requiere app corriendo)
            # Namespace: root\OpenHardwareMonitor
            ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = ohm.Sensor()
            for sensor in sensors:
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    return float(sensor.Value)
        except:
            pass # OHM no disponible

        try:
            # Opción B: WMI Estándar (MSAcpi)
            # Devuelve décimas de Kelvin. (K - 273.2) = Celsius
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                kelvin = temps[0].CurrentTemperature
                celsius = (kelvin - 2732) / 10.0
                if celsius > 0: return celsius
        except:
            pass

    # 2. Estrategia General: psutil
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Retorna la primera temperatura disponible
            return next(iter(temps.values()))[0].current
    except:
        pass
    
    return 0.0

def enviar_datos():
    """Recopila métricas y las envía al servidor central con lógica de reintentos."""
    intentos_fallidos = 0
    
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "temp": obtener_temperatura()
            }
            
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT, verify=VERIFICAR_SSL)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)
            
            # Verificar si el servidor nos envió un comando en la respuesta
            respuesta_json = response.json()
            if respuesta_json.get("comando") == "reiniciar":
                print(f"⚠️  COMANDO RECIBIDO: Reiniciando servidor en 5 segundos...")
                time.sleep(5)
                if os.name == 'nt': # Windows
                    os.system("shutdown /r /t 0 /f")
                else: # Linux / Otros
                    os.system("shutdown -r now")

            print(f"✓ Datos enviados - CPU: {metricas['cpu']:.1f}% | RAM: {metricas['ram']:.1f}% | Temp: {metricas['temp']:.1f}°C")
            intentos_fallidos = 0 # Reiniciar contador en éxito

        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            intentos_fallidos += 1
            if isinstance(e, requests.exceptions.ConnectTimeout):
                print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Timeout. El servidor no responde.")
            elif isinstance(e, requests.exceptions.ConnectionError):
                print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Error de conexión. ¿Servidor encendido?")
            elif isinstance(e, requests.exceptions.HTTPError):
                 print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Error del servidor ({e.response.status_code}).")
            else:
                print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Error de red: {e}")

            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Se superó el máximo de reintentos. Esperando {AGENTE_ESPERA_REINTENTO}s...")
                time.sleep(AGENTE_ESPERA_REINTENTO)
                intentos_fallidos = 0 # Reiniciar contador para el próximo ciclo
        except Exception as e:
            print(f"⚠️ Ocurrió un error inesperado: {e}")
            
        time.sleep(AGENTE_INTERVALO)

if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        print(f"\n[ERROR] El agente se detuvo: {e}")
        input("Presione ENTER para salir...")  