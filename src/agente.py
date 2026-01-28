"""Agente remoto: recopila métricas del servidor y las envía a la central"""
import psutil
import requests
import time
import socket
import sys
from pathlib import Path

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

def enviar_datos():
    """Recopila métricas cada AGENTE_INTERVALO segundos y las envía al servidor central"""
    intentos_fallidos = 0
    
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),      # % de CPU
                "ram": psutil.virtual_memory().percent,     # % de RAM
                "temp": 0.0                                 # Temperatura (no disponible)
            }
            
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT)
            
            if response.status_code == 200:
                print(f"✓ Datos enviados - CPU: {metricas['cpu']}% | RAM: {metricas['ram']}%")
                intentos_fallidos = 0
            else:
                print(f"✗ Error: {response.status_code}")
                intentos_fallidos += 1
                
        except Exception as e:
            intentos_fallidos += 1
            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Sin conexión al servidor (reintentando cada {AGENTE_ESPERA_REINTENTO}s)")
                intentos_fallidos = 0
            
        time.sleep(AGENTE_INTERVALO)

if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        print(f"\n[ERROR] El agente se detuvo: {e}")
        input("Presione ENTER para salir...")