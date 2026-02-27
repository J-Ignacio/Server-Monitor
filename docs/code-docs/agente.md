# Documentación Técnica: Agente de Monitoreo

Este documento detalla el funcionamiento del Agente de Monitoreo, incluyendo tanto la lógica de recolección de datos (`agente.py`) como el wrapper para ejecutarse como Servicio de Windows (`agente_servicio.py`).

## 1. Código Fuente Completo: Lógica del Agente (`src/agente.py`)

```python
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
    from config import URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT, AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO, VERIFICAR_SSL, LOGS_HABILITADOS, BASE_DIR
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
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def obtener_temperatura():
    """Intenta obtener la temperatura de la CPU (Soporta WMI/OHM)"""
    # 1. Estrategia Windows: WMI
    if wmi:
        try:
            # Opción A: OpenHardwareMonitor / LibreHardwareMonitor
            # Namespaces: root\OpenHardwareMonitor, root\LibreHardwareMonitor
            ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor") # Se prueba ambos en bucle
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

def ejecutar_diagnostico():
    """Imprime en consola qué sensores se detectan al iniciar"""
    print("\n🔍 --- DIAGNÓSTICO DE SENSORES ---")
    # ... lógica de detección de WMI y sensores ...
    print("-----------------------------------\n")

def enviar_datos(stop_event=None):
    """Recopila métricas y las envía al servidor central con lógica de reintentos."""
    configurar_logger()
    
    hostname = socket.gethostname().strip()
    ip_real = obtener_ip_real().strip()
    ID_SERVIDOR = f"{hostname} ({ip_real})"

    # Inicializar COM para WMI (Vital para hilos/servicios)
    if wmi and pythoncom:
        try:
            pythoncom.CoInitialize()
        except: pass

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
```

- Lógica de Negocio: Se prioriza el Método 1 sobre el 2 porque `MSAcpi` a menudo reporta valores estáticos si el fabricante de la BIOS no expone correctamente las zonas térmicas.

- Matemática de Precisión: El cálculo `(K - 2732) / 10.0` es fundamental ya que los sensores térmicos bajo el estándar ACPI suelen devolver valores en $10^{-1}$ Kelvin.

### 4. Bucle de Telemetría y Resiliencia de Red

El núcleo del agente, encargado de la captura de datos y la gestión de la comunicación HTTP.

```python
def enviar_datos():
    """Bucle infinito de reporte con manejo de estados de error"""
    intentos_fallidos = 0
    
    while True:
        try:
            metricas = {
                "id_servidor": ID_SERVIDOR,
                "cpu": psutil.cpu_percent(interval=1),      # Bloquea 1s para promedio real
                "ram": psutil.virtual_memory().percent,     # Snapshot del % de uso RAM
                "temp": obtener_temperatura()               # Valor calculado en el bloque anterior
            }
            
            # Envío de carga útil (Payload) vía POST
            response = requests.post(URL_REPORTAR, json=metricas, timeout=AGENTE_TIMEOUT)
            
            if response.status_code == 200:
                print(f"✓ Datos enviados exitosamente")
                intentos_fallidos = 0
            else:
                intentos_fallidos += 1

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
            # Lógica de reintento exponencial o espera
            intentos_fallidos += 1
            if intentos_fallidos >= AGENTE_REINTENTOS:
                print(f"✗ Servidor inalcanzable. Esperando {AGENTE_ESPERA_REINTENTO}s...")
                intentos_fallidos = 0 # Reinicio del contador para evitar overflow
                time.sleep(AGENTE_ESPERA_REINTENTO)
        
        time.sleep(AGENTE_INTERVALO)

```

- Métrica de CPU: `psutil.cpu_percent(interval=1)` es vital. Si el intervalo fuera 0, la métrica sería un pico instantáneo sin valor estadístico. Un segundo permite promediar los ciclos de los hilos de ejecución.

- Gestión de Red: Se capturan excepciones específicas de `requests`. Esto evita que el agente colapse ante micro-cortes de internet o reinicios programados del servidor central.

### 5. Punto de Entrada del Script

Protección del flujo de ejecución principal.

```python
if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        # Captura cualquier error no controlado para evitar cierre súbito de terminal
        print(f"\n[ERROR CRÍTICO] El agente se detuvo: {e}")
        input("Presione ENTER para salir...")
```

### 6. Ejecución como Servicio de Windows

Para entornos de producción, el agente se ejecuta como un servicio en segundo plano.

## 2. Código Fuente Completo: Servicio de Windows (`src/agente_servicio.py`)

Este archivo actúa como un "wrapper" o envoltorio que permite a Windows gestionar el script de Python como un servicio en segundo plano (sin ventana).

```python
"""
Wrapper para ejecutar el Agente como Servicio de Windows.
Requiere permisos de Administrador para instalarse.
"""
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import threading
from pathlib import Path

# Asegurar que podemos importar el módulo 'agente' desde el mismo directorio
if getattr(sys, 'frozen', False):
    # Si corre como .exe
    base_path = Path(sys.executable).parent
else:
    # Si corre como script .py
    base_path = Path(__file__).resolve().parent

sys.path.append(str(base_path))

from agente import enviar_datos


class AgenteService(win32serviceutil.ServiceFramework):
    _svc_name_ = "NOCMonitorAgente"
    _svc_display_name_ = "NOC Monitor Agente"
    _svc_description_ = "Envía métricas de CPU/RAM/Disco al servidor central NOC."

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
            servicemanager.LogErrorMsg(f"Error fatal en agente: {e}")


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AgenteService)
```

### Explicación Técnica
- **Wrapper (`agente_servicio.py`):** Utiliza la librería `pywin32` para interactuar con el Service Control Manager (SCM) de Windows.
- **Señal de Parada:** El servicio envía un evento de threading (`stop_event`) a la función `enviar_datos()` para permitir un cierre limpio sin matar el proceso abruptamente.
- **Instalación:** Se gestiona mediante el script `instalar_agente.bat` que registra el servicio con inicio automático.
```

- Finalidad: El bloque `if __name__ == "__main__":` previene que el agente comience a recolectar datos si el archivo es importado accidentalmente por otro script. `El input()` final es una cortesía para usuarios de Windows, permitiéndoles leer el error antes de que la ventana de consola desaparezca