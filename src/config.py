"""
Archivo de configuración centralizado para el sistema de monitoreo
Editar este archivo para cambiar la configuración sin tocar el código
"""
import os
import json
from pathlib import Path

# Detectar sistema operativo
SISTEMA_OPERATIVO = "Windows" if os.name == 'nt' else "Linux/Unix"

# Rutas de archivos de configuración
CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Crear directorio de configuración si no existe
CONFIG_DIR.mkdir(exist_ok=True)

# Configuración predeterminada
CONFIGURACION_PREDETERMINADA = {
    "servidor_central": {
        "ip": "127.0.0.1",
        "puerto": 8000,
        "host": "0.0.0.0"
    },
    "agente": {
        "intervalo_envio": 5,  # segundos
        "timeout": 5,  # segundos
        "reintentos": 3,
        "espera_reintento": 5  # segundos
    },
    "dashboard": {
        "intervalo_actualizacion": 2,  # segundos
        "host": "localhost",
        "puerto": 8501
    },
    "sistema": {
        "debug": False,
        "logs_habilitados": True,
        "archivo_log": "logs/sistema.log"
    }
}

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

# Cargar configuración al importar
CONFIG = cargar_config()

# Variables de configuración para acceso rápido
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

# URL completa del servidor central
URL_REPORTAR = f"http://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/reportar"
URL_ESTADO = f"http://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/estado"

if DEBUG:
    print(f"🔧 Modo DEBUG activo")
    print(f"📁 Sistema: {SISTEMA_OPERATIVO}")
    print(f"⚙️  Configuración: {CONFIG_FILE}")
