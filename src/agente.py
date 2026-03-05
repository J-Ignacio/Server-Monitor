"""Agente remoto: recopila métricas del servidor y las envía a la central"""
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

# Intento de importar WMI para soporte de temperatura en Windows
try:
    import wmi
    import pythoncom
except ImportError:
    wmi = None
    pythoncom = None

try:
    from config import URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT, AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO, VERIFICAR_SSL, LOGS_HABILITADOS, BASE_DIR, AGENTE_IP_MANUAL, SERVIDOR_CENTRAL_IP, SERVIDOR_CENTRAL_PUERTO
except Exception as e:
    print(f"\n[ERROR FATAL] No se pudo cargar la configuración: {e}")
    print("Posible causa: Falta de permisos para crear 'config.json' o carpeta 'config'.")
    input("Presione ENTER para salir...")
    sys.exit(1)

# --- Configuración de Logging ---
def configurar_logger():
    handlers = [logging.StreamHandler(sys.stdout)] # Siempre mostrar en consola
    
    if LOGS_HABILITADOS:
        log_dir = BASE_DIR / "logs"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "agente.log"
        
        # Rota el archivo cuando llega a 1MB, guarda hasta 3 copias antiguas
        handlers.append(RotatingFileHandler(str(log_file), maxBytes=1_000_000, backupCount=3, encoding='utf-8'))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )

# Detecta la IP real del servidor en la red local
def obtener_ip_real():
    """Obtiene la IP local del servidor"""
    # Si se configuró una IP manual, usarla directamente
    if AGENTE_IP_MANUAL:
        return AGENTE_IP_MANUAL

    try:
        # Intentar conectar al servidor central para ver qué interfaz usa el OS
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((SERVIDOR_CENTRAL_IP, SERVIDOR_CENTRAL_PUERTO))
        IP = s.getsockname()[0]
        s.close()
    except Exception:
        # Fallback: Intentar Google DNS si falla lo anterior
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            IP = s.getsockname()[0]
            s.close()
        except Exception:
            IP = '127.0.0.1'
    return IP

def obtener_temperatura():
    """Intenta obtener la temperatura de la CPU (Soporta WMI/OHM)"""
    # 1. Estrategia Windows: WMI
    if wmi:
        # Probar OpenHardwareMonitor y LibreHardwareMonitor
        namespaces = ["root\\OpenHardwareMonitor", "root\\LibreHardwareMonitor"]
        for ns in namespaces:
            try:
                ohm = wmi.WMI(namespace=ns)
                sensors = ohm.Sensor()
                for sensor in sensors:
                    if sensor.SensorType == 'Temperature':
                        # Búsqueda más flexible (CPU, Core, Package, Tctl, Tdie)
                        nombre = sensor.Name.upper()
                        if any(x in nombre for x in ['CPU', 'CORE', 'PACKAGE', 'TCTL', 'TDIE']):
                            return float(sensor.Value)
            except:
                continue

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

def ejecutar_diagnostico():
    """Imprime en consola qué sensores se detectan al iniciar"""
    print("\n🔍 --- DIAGNÓSTICO DE SENSORES ---")
    if not wmi:
        print("❌ Librería 'wmi' no detectada.")
        return

    namespaces = ["root\\OpenHardwareMonitor", "root\\LibreHardwareMonitor"]
    encontrado = False

    for ns in namespaces:
        try:
            ohm = wmi.WMI(namespace=ns)
            sensores = ohm.Sensor()
            if sensores:
                print(f"✅ Conexión con {ns}: EXITOSA")
                encontrado = True
                temps = [s for s in sensores if s.SensorType == 'Temperature']
                if temps:
                    print("   Sensores de temperatura encontrados:")
                    for s in temps:
                        print(f"   - Nombre: '{s.Name}' | Valor: {s.Value}°C")
                else:
                    print("   ⚠️ Conectado, pero NO hay sensores de temperatura.")
        except:
            pass
    
    if not encontrado:
        print(f"⚠️ No se detectó Open Hardware Monitor ni Libre Hardware Monitor activos.")
        print(f"   Asegúrate de ejecutarlo como Administrador.")
    print("-----------------------------------\n")

def enviar_datos(stop_event=None):
    """Recopila métricas y las envía al servidor central con lógica de reintentos."""
    configurar_logger()

    # Inicializar COM para WMI al principio (Vital para evitar errores de inicialización)
    if wmi and pythoncom:
        try:
            pythoncom.CoInitialize()
        except:
            pass
    
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
    logging.info(f"🚀 Agente iniciado: {ID_SERVIDOR}")
    logging.info(f"📡 Reportando a: {URL_REPORTAR}")
    logging.info(f"⏱️  Intervalo: {AGENTE_INTERVALO}s | Temp: {'WMI' if wmi else 'Nativo'}")

    # Ejecutar diagnóstico visual al arrancar
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
            
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT, verify=VERIFICAR_SSL)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)
            
            # Verificar si el servidor nos envió un comando en la respuesta
            respuesta_json = response.json()
            if respuesta_json.get("comando") == "reiniciar":
                print(f"⚠️  COMANDO RECIBIDO: Reiniciando servidor en 5 segundos...")
                logging.warning(f"⚠️  COMANDO RECIBIDO: Reiniciando servidor en 5 segundos...")
                time.sleep(5)
                if os.name == 'nt': # Windows
                    os.system("shutdown /r /t 0 /f")
                else: # Linux / Otros
                    os.system("shutdown -r now")

            print(f"✓ Datos enviados - CPU: {metricas['cpu']:.1f}% | RAM: {metricas['ram']:.1f}% | Disk: {metricas['disk']:.1f}%")
            logging.info(f"✓ Enviado - CPU: {metricas['cpu']}% | RAM: {metricas['ram']}% | Disk: {metricas['disk']}% | Temp: {metricas['temp']:.1f}°C")
            intentos_fallidos = 0 # Reiniciar contador en éxito

        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            intentos_fallidos += 1
            msg_error = f"Error de conexión ({intentos_fallidos}/{AGENTE_REINTENTOS}): {e}"
            
            if isinstance(e, requests.exceptions.ConnectTimeout):
                print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Timeout. El servidor no responde.")
                msg_error = "Timeout: El servidor central no responde."
            elif isinstance(e, requests.exceptions.ConnectionError):
                print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Error de conexión. ¿Servidor encendido?")
            elif isinstance(e, requests.exceptions.HTTPError):
                 print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Error del servidor ({e.response.status_code}).")
            else:
                print(f"⚠️  Intento {intentos_fallidos}/{AGENTE_REINTENTOS}: Error de red: {e}")
                msg_error = "Conexión rechazada: ¿El servidor central está encendido?"
            
            logging.warning(f"⚠️ {msg_error}")

            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Se superó el máximo de reintentos. Esperando {AGENTE_ESPERA_REINTENTO}s...")
                logging.error(f"✗ Límite de reintentos alcanzado. Pausando {AGENTE_ESPERA_REINTENTO}s...")
                time.sleep(AGENTE_ESPERA_REINTENTO)
                intentos_fallidos = 0 # Reiniciar contador para el próximo ciclo
        except Exception as e:
            print(f"⚠️ Ocurrió un error inesperado: {e}")
            logging.exception(f"⚠️ Error inesperado: {e}")
            
        if stop_event:
            if stop_event.wait(AGENTE_INTERVALO):
                break
        else:
            time.sleep(AGENTE_INTERVALO)

if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        print(f"\n[ERROR] El agente se detuvo: {e}")
        logging.critical(f"🛑 El agente se detuvo por error crítico: {e}")
        input("Presione ENTER para salir...")