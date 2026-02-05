# Documentación Técnica: Agente de Monitoreo `(agente.py)`

El agente es un script de telemetría diseñado para ejecutarse de forma persistente. Su función es transformar el estado del hardware en datos estructurados (JSON) y transmitirlos mediante una arquitectura cliente-servidor.

## 🛠️ Análisis Detallado por Módulos

### 1. Inicialización y Gestión de Dependencias

Esta sección asegura que el entorno de ejecución tenga las herramientas necesarias y maneja la compatibilidad entre Sistemas Operativos.

```
"""Agente remoto: recopila métricas del servidor y las envía a la central"""
import psutil      # Interfaz de bajo nivel para estadísticas de sistema
import requests    # Cliente HTTP para comunicación con la API
import time        # Gestión de retardos y timers
import socket      # Primitivas de red para identificación de host
import sys         # Control de flujos de salida y sistema
from pathlib import Path

# Carga condicional de WMI (Windows Management Instrumentation)
try:
    import wmi
except ImportError:
    wmi = None

# Carga de constantes desde módulo local 'config'
try:
    from config import URL_REPORTAR, AGENTE_INTERVALO, AGENTE_TIMEOUT, AGENTE_REINTENTOS, AGENTE_ESPERA_REINTENTO
except Exception as e:
    print(f"\n[ERROR FATAL] No se pudo cargar la configuración: {e}")
    print("Posible causa: Falta de permisos para crear 'config.json' o carpeta 'config'.")
    input("Presione ENTER para salir...")
    sys.exit(1)
```

- Análisis de Seguridad: El uso de sys.exit(1) garantiza que el programa no entre en un estado inconsistente si faltan variables críticas. El código 1 indica una salida por error.

- Abstracción de SO: El bloque try/except de la librería wmi permite que el agente sea agnóstico al sistema operativo, evitando errores de "Módulo no encontrado" en entornos Linux/Unix.

### 2. Algoritmo de Identificación de Red

Para garantizar que la central identifique correctamente la procedencia de los datos, el agente calcula su identidad dinámicamente.

```
def obtener_ip_real():
    """Detecta la interfaz de red activa mediante un socket efímero"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No requiere conexión real, solo fuerza al SO a elegir una interfaz de salida
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback a bucle local si no hay red activa
    finally:
        s.close() # Liberación de recursos del sistema
    return IP

hostname = socket.gethostname()
ID_SERVIDOR = f"{hostname} ({obtener_ip_real()})"
```
- Eficiencia Técnica: Se utiliza el protocolo UDP (SOCK_DGRAM) porque es más rápido y no requiere un apretón de manos (handshake) completo para determinar la ruta de salida.

- Contexto de Identidad: El ID_SERVIDOR combina el nombre de red del equipo con su IP actual, lo que facilita el filtrado en bases de datos si el servidor tiene múltiples interfaces.

### 3. Jerarquía de Sensores Térmicos

Extraer la temperatura en Windows es un reto técnico debido a las restricciones del kernel. Este bloque implementa tres estrategias de respaldo.

```
def obtener_temperatura():
    """Estrategias en cascada para la obtención de métricas térmicas"""
    if wmi:
        # MÉTODO 1: Integración con OpenHardwareMonitor (vía WMI)
        try:
            ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            sensors = ohm.Sensor()
            for sensor in sensors:
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    return float(sensor.Value)
        except:
            pass 

        # MÉTODO 2: API de ACPI (Advanced Configuration and Power Interface)
        try:
            w = wmi.WMI(namespace="root\\wmi")
            temps = w.MSAcpi_ThermalZoneTemperature()
            if temps:
                # Conversión: décimas de Kelvin a grados Celsius
                kelvin_x_10 = temps[0].CurrentTemperature
                celsius = (kelvin_x_10 - 2732) / 10.0
                if celsius > 0: return celsius
        except:
            pass

    # MÉTODO 3: Fallback multiplataforma (psutil)
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            return next(iter(temps.values()))[0].current
    except:
        pass
    
    return 0.0
```

- Lógica de Negocio: Se prioriza el Método 1 sobre el 2 porque MSAcpi a menudo reporta valores estáticos si el fabricante de la BIOS no expone correctamente las zonas térmicas.

- Matemática de Precisión: El cálculo (K - 2732) / 10.0 es fundamental ya que los sensores térmicos bajo el estándar ACPI suelen devolver valores en $10^{-1}$ Kelvin.

### 4. Bucle de Telemetría y Resiliencia de Red

El núcleo del agente, encargado de la captura de datos y la gestión de la comunicación HTTP.

```
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

- Métrica de CPU: psutil.cpu_percent(interval=1) es vital. Si el intervalo fuera 0, la métrica sería un pico instantáneo sin valor estadístico. Un segundo permite promediar los ciclos de los hilos de ejecución.

- Gestión de Red: Se capturan excepciones específicas de requests. Esto evita que el agente colapse ante micro-cortes de internet o reinicios programados del servidor central.

### 5. Punto de Entrada del Script

Protección del flujo de ejecución principal.

```
if __name__ == "__main__":
    try:
        enviar_datos()
    except Exception as e:
        # Captura cualquier error no controlado para evitar cierre súbito de terminal
        print(f"\n[ERROR CRÍTICO] El agente se detuvo: {e}")
        input("Presione ENTER para salir...")
```

- Finalidad: El bloque if __name__ == "__main__": previene que el agente comience a recolectar datos si el archivo es importado accidentalmente por otro script. El input() final es una cortesía para usuarios de Windows, permitiéndoles leer el error antes de que la ventana de consola desaparezca