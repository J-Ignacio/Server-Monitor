"""Agente remoto: recopila métricas del servidor y las envía a la central"""
import psutil
import requests
import time
import socket
import sys
from pathlib import Path

# Intento de importar WMI para soporte de temperatura en Windows
try:
    import wmi
except ImportError:
    wmi = None

try:
    from config import URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT, AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO
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
hostname = socket.gethostname()
ID_SERVIDOR = f"{hostname} ({obtener_ip_real()})"

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
    """Recopila métricas cada AGENTE_INTERVALO segundos y las envía al servidor central"""
    intentos_fallidos = 0
    
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),      # % de CPU
                "ram": psutil.virtual_memory().percent,     # % de RAM
                "temp": obtener_temperatura()               # Temperatura
            }
            
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT)
            
            if response.status_code == 200:
                print(f"✓ Datos enviados - CPU: {metricas['cpu']}% | RAM: {metricas['ram']}% | Temp: {metricas['temp']}°C")
                intentos_fallidos = 0
            else:
                print(f"✗ Error: {response.status_code}")
                intentos_fallidos += 1

        except requests.exceptions.ConnectTimeout:
            print(f"⚠️ Intento fallido: Timeout. El servidor no responde. (Revisa el Firewall en {URL_REPORTAR.split('/')[2]})")
            intentos_fallidos += 1
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Intento fallido: Error de conexión. ¿Está el servidor encendido y conectado a la red?")
            intentos_fallidos += 1
            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Sin conexión al servidor (reintentando cada {AGENTE_ESPERA_REINTENTO}s)")
                intentos_fallidos = 0
        except Exception as e:
            print(f"⚠️ Intento fallido: {e}")
            
        time.sleep(AGENTE_INTERVALO)

if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        print(f"\n[ERROR] El agente se detuvo: {e}")
        input("Presione ENTER para salir...")