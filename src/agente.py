import psutil
import requests
import time
import socket

# --- CONFIGURACIÓN ---
IP_CENTRAL = "192.168.4.143" 
PUERTO = "8000"
URL = f"http://{IP_CENTRAL}:{PUERTO}/reportar"

# --- NUEVA FUNCIÓN PARA DETECTAR LA IP CORRECTA ---
def obtener_ip_real():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita conexión real, solo ayuda a Python a ver qué tarjeta de red sale a internet
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# --- CONFIGURACIÓN DEL NOMBRE ---
hostname = socket.gethostname()
# Aquí llamamos a la función que acabamos de crear arriba
ID_SERVIDOR = f"{hostname} ({obtener_ip_real()})" 

print(f"🚀 Agente iniciado: {ID_SERVIDOR}")
print(f"📡 Reportando a: {URL}")

def enviar_datos():
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),
                "ram": psutil.virtual_memory().percent,
                "temp": 0.0 
            }
            
            response = requests.post(URL, json=metricas, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Datos enviados de {ID_SERVIDOR}")
            else:
                print(f"⚠️ Error en servidor: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Sin conexión con la central... (Reintentando en 5s)")
            
        time.sleep(5)

if __name__ == "__main__":
    enviar_datos()