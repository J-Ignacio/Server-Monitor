import psutil
import requests
import time
import socket

# CONFIGURACIÓN CRÍTICA
# 1. Si usas Hamachi, pon aquí tu IP de Hamachi.
# 2. Si es en la misma red, pon tu IP local (ipconfig).
# 3. Si pruebas en la misma PC, deja "127.0.0.1".
IP_CENTRAL = "127.0.0.1" 
URL_SERVIDOR = f"http://{IP_CENTRAL}:8000/reportar"

# Obtiene el nombre del equipo automáticamente
nombre_equipo = socket.gethostname()

print(f"🚀 Agente iniciado en: {nombre_equipo}")
print(f"📡 Enviando datos a: {URL_SERVIDOR}")

while True:
    try:
        # Captura de métricas
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        
        # Captura de temperatura protegida
        temp = 0.0
        try:
            if hasattr(psutil, "sensors_temperatures"):
                t = psutil.sensors_temperatures()
                if t:
                    for name, entries in t.items():
                        temp = entries[0].current
                        break
        except:
            temp = 0.0

        # Creación del paquete (JSON)
        payload = {
            "id_servidor": nombre_equipo,
            "cpu": cpu,
            "ram": ram,
            "temp": temp
        }
        
        # Envío a la API
        res = requests.post(URL_SERVIDOR, json=payload, timeout=3)
        
        if res.status_code == 200:
            print(f"✅ [{time.strftime('%H:%M:%S')}] Datos enviados correctamente.")

    except Exception as e:
        print(f"❌ Error de conexión: {e}. Reintentando...")
    
    # Pausa de 5 segundos antes de la siguiente actualización
    time.sleep(5)