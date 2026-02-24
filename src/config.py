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

# Configuración predeterminada
CONFIGURACION_PREDETERMINADA = {
    "servidor_central": {
        "ip": "192.168.4.100",  # <--- IP Actualizada
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
    },
    "email": {
        "habilitado": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "usuario": "tu_correo@gmail.com",
        "password": "tu_contraseña_de_aplicacion",
        "destinatario": "admin@empresa.com"
    },
    "seguridad": {
        "usar_ssl": False,
        "archivo_cert": "certs/cert.pem",
        "archivo_key": "certs/key.pem",
        "verificar_ssl": False
    }
}

def _fusionar_configs(cargada, predeterminada):
    """
    Fusiona recursivamente la configuración predeterminada en la cargada,
    añadiendo solo las claves que falten sin sobreescribir las existentes.
    Retorna True si se hizo alguna modificación.
    """
    modificado = False
    for key, value in predeterminada.items():
        if key not in cargada:
            cargada[key] = value
            modificado = True
        elif isinstance(value, dict) and isinstance(cargada.get(key), dict):
            if _fusionar_configs(cargada[key], value):
                modificado = True
    return modificado

def cargar_config():
    """
    Carga la configuración desde JSON. Si no existe, lo crea.
    Si está corrupto, lo renombra. Si es antiguo, añade las nuevas claves.
    """
    config_cargada = CONFIGURACION_PREDETERMINADA.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_leida = json.load(f)
            # Fusionar para añadir claves de nuevas versiones sin borrar las antiguas
            if _fusionar_configs(config_leida, CONFIGURACION_PREDETERMINADA):
                # print(f"🔧 Configuración actualizada con nuevas claves. Guardando...")
                guardar_config(config_leida)
            return config_leida
        except json.JSONDecodeError as e:
            print(f"❌ Error: El archivo '{CONFIG_FILE}' está corrupto: {e}")
            mal_config_path = CONFIG_FILE.with_suffix('.json.bad')
            try:
                CONFIG_FILE.rename(mal_config_path)
                print(f"   -> El archivo dañado ha sido renombrado a '{mal_config_path.name}'")
            except OSError as rename_error:
                print(f"   -> No se pudo renombrar el archivo dañado: {rename_error}")
            print("   -> Se usará y guardará la configuración predeterminada.")
            guardar_config(config_cargada)
            return config_cargada
        except Exception as e:
            print(f"⚠️  Error inesperado al cargar configuración: {e}")
            print("   Usando configuración predeterminada...")
            return config_cargada
    else:
        # Si no existe, crear con valores predeterminados
        # print("✓ No se encontró config.json, creando uno nuevo con valores predeterminados.")
        guardar_config(CONFIGURACION_PREDETERMINADA)
        return config_cargada

def guardar_config(config):
    """Guarda la configuración en archivo JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        # print(f"✓ Configuración guardada en: {CONFIG_FILE}")
    except Exception as e:
        print(f"✗ Error al guardar configuración: {e}")

# Cargar configuración al importar
CONFIG = cargar_config()

# Parche de compatibilidad: Si config.json es viejo y no tiene email, agregarlo
if "email" not in CONFIG:
    CONFIG["email"] = CONFIGURACION_PREDETERMINADA["email"]
    guardar_config(CONFIG)

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

EMAIL_CONFIG = CONFIG["email"]

# Configuración de Seguridad
SEGURIDAD = CONFIG.get("seguridad", CONFIGURACION_PREDETERMINADA["seguridad"])
USAR_SSL = SEGURIDAD.get("usar_ssl", False)
SSL_CERT = BASE_DIR / SEGURIDAD.get("archivo_cert", "certs/cert.pem")
SSL_KEY = BASE_DIR / SEGURIDAD.get("archivo_key", "certs/key.pem")
VERIFICAR_SSL = SEGURIDAD.get("verificar_ssl", False)

# URL completa del servidor central
PROTOCOLO = "https" if USAR_SSL else "http"
URL_REPORTAR = f"{PROTOCOLO}://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/reportar"
URL_ESTADO = f"{PROTOCOLO}://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/estado"

if DEBUG:
    print(f"🔧 Modo DEBUG activo")
    print(f"📁 Sistema: {SISTEMA_OPERATIVO}")
    print(f"⚙️  Configuración: {CONFIG_FILE}")
