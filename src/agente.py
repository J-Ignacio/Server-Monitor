"""Agente remoto: recopila métricas del servidor y las envía a la central"""
import psutil
import requests
import time
import socket

# Configuración del servidor central donde reportar
IP_CENTRAL = "192.168.4.143"  # Cambiar con la IP de la laptop NOC
PUERTO = "8000"
URL = f"http://{IP_CENTRAL}:{PUERTO}/reportar"

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
print(f"✓ Reportando a: {URL}")

def enviar_datos():
    """Recopila métricas cada 5s y las envía al servidor central"""
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),      # % de CPU
                "ram": psutil.virtual_memory().percent,     # % de RAM
                "temp": 0.0                                 # Temperatura (no disponible)
            }
            
            response = requests.post(URL, json=metricas, timeout=5)
            
            if response.status_code == 200:
                print(f"✓ Datos enviados")
            else:
                print(f"✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Sin conexión (reintentando en 5s)")
            
        time.sleep(5)

if __name__ == "__main__":
    enviar_datos()