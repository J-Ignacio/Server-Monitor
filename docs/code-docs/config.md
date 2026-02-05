# Documentación Técnica: Configuración Centralizada `(config.py)`
Este módulo gestiona la persistencia de los ajustes del sistema en un archivo JSON. Su objetivo es permitir cambios en el comportamiento del agente, el servidor o el dashboard sin necesidad de modificar el código fuente de los mismos.

## 🛠️ Análisis Detallado por Módulos

### 1. Gestión de Rutas y Compatibilidad con Ejecutables

Esta sección es crítica para que el programa funcione tanto como script de Python como cuando se empaqueta en un archivo `.exe`.

```
"""
Archivo de configuración centralizado para el sistema de monitoreo
Editar este archivo para cambiar la configuración sin tocar el código
"""
import os
import json
import sys
from pathlib import Path

# Detectar sistema operativo
SISTEMA_OPERATIVO = "Windows"

# Rutas de archivos de configuración
if getattr(sys, 'frozen', False):
    # Si estamos ejecutando como .exe (PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # Si estamos ejecutando como script .py normal
    BASE_DIR = Path(__file__).parent.parent

CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Crear directorio de configuración si no existe
CONFIG_DIR.mkdir(exist_ok=True)

# Configuración de Base de Datos
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_FILE = DATA_DIR / "metricas.db"
```

- Análisis de `sys.frozen`: PyInstaller usa esta bandera para indicar que el script está empaquetado. El código detecta esto para que las carpetas `/config` y `/data` se creen siempre junto al archivo ejecutable, evitando errores de "Ruta no encontrada".

- Uso de `pathlib`: Se prefiere `Path` sobre `os.path` por su manejo de rutas como objetos, lo que facilita la concatenación con el operador `/` y mejora la legibilidad.

- Persistencia de Datos: Define `DB_FILE`, que será la ubicación física de la base de datos SQLite donde el servidor guardará las métricas.

### 2. Definición de Valores Predeterminados

Si el archivo de configuración se pierde o se borra, el sistema es capaz de autorepararse usando este diccionario.

```
# Configuración predeterminada
CONFIGURACION_PREDETERMINADA = {
    "servidor_central": {
        "ip": "192.168.4.175",  # IP donde el servidor escucha
        "puerto": 8000,
        "host": "0.0.0.0"       # Permite conexiones externas
    },
    "agente": {
        "intervalo_envio": 5,   # Frecuencia de envío (segundos)
        "timeout": 5,           # Tiempo límite de espera de respuesta
        "reintentos": 3,        # Reintentos antes de marcar error
        "espera_reintento": 5   # Pausa tras fallo de red
    },
    "dashboard": {
        "intervalo_actualizacion": 2, # Refresco visual del Dashboard
        "host": "localhost",
        "puerto": 8501
    },
    "sistema": {
        "debug": False,
        "logs_habilitados": True,
        "archivo_log": "logs/sistema.log"
    }
}
```

- Lógica de Red: El host: `"0.0.0.0"` en el servidor es vital; indica que el servidor aceptará conexiones de cualquier dispositivo en la red local, no solo del propio equipo.

- Optimización del Agente: El `intervalo_envio: 5` establece un equilibrio entre tener datos en tiempo real y no saturar el tráfico de red.

### 3. Funciones de Carga y Guardado (Serialización JSON)

Estas funciones manejan la lectura y escritura en disco, asegurando que los cambios del usuario persistan.

```
def cargar_config():
    """Carga la configuración desde el archivo JSON"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error al cargar configuración: {e}")
            print("   Usando configuración predeterminada...")
            return CONFIGURACION_PREDETERMINADA.copy()
    else:
        # Si no existe, crear con valores predeterminados
        guardar_config(CONFIGURACION_PREDETERMINADA)
        return CONFIGURACION_PREDETERMINADA.copy()

def guardar_config(config):
    """Guarda la configuración en archivo JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"✓ Configuración guardada en: {CONFIG_FILE}")
    except Exception as e:
        print(f"✗ Error al guardar configuración: {e}")
```

- Codificación UTF-8: Se especifica `encoding='utf-8'` para evitar errores con caracteres especiales (como tildes o la "ñ") en las rutas o logs.

- Auto-generación: Si el archivo `config.json` no existe en la primera ejecución, la función `cargar_config` lo crea automáticamente llamando a `guardar_config`.

### 4. Exportación de Variables de Acceso Rápido

Para facilitar la lectura en otros archivos (como el agente o el servidor), el script descompone el diccionario en constantes directas.

```
# Cargar configuración al importar el módulo
CONFIG = cargar_config()

# Variables de configuración para acceso rápido (Unpacking)
SERVIDOR_CENTRAL_IP = CONFIG["servidor_central"]["ip"]
SERVIDOR_CENTRAL_PUERTO = CONFIG["servidor_central"]["puerto"]
SERVIDOR_CENTRAL_HOST = CONFIG["servidor_central"]["host"]

AGENTE_INTERVALO = CONFIG["agente"]["intervalo_envio"]
AGENTE_TIMEOUT = CONFIG["agente"]["timeout"]
AGENTE_REINTENTOS = CONFIG["agente"]["reintentos"]
AGENTE_ESPERA_REINTENTO = CONFIG["agente"]["espera_reintento"]

DASHBOARD_INTERVALO = CONFIG["dashboard"]["intervalo_actualizacion"]
DASHBOARD_HOST = CONFIG["dashboard"]["host"]
DASHBOARD_PUERTO = CONFIG["dashboard"]["puerto"]

DEBUG = CONFIG["sistema"]["debug"]
LOGS_HABILITADOS = CONFIG["sistema"]["logs_habilitados"]
ARCHIVO_LOG = CONFIG["sistema"]["archivo_log"]

# Construcción dinámica de URLs
URL_REPORTAR = f"http://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/reportar"
URL_ESTADO = f"http://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/estado"

if DEBUG:
    print(f"🔧 Modo DEBUG activo")
    print(f"📁 Sistema: {SISTEMA_OPERATIVO}")
    print(f"⚙️  Configuración: {CONFIG_FILE}")
```

- Construcción de URLs: Define `URL_REPORTAR` dinámicamente. Si el usuario cambia la IP en el JSON, el agente automáticamente sabrá a dónde enviar los datos sin tocar una sola línea de lógica.

- Modo Debug: Al activar `DEBUG: True`, el sistema imprime información extra en la consola, ideal para resolver problemas de conexión durante la instalación.