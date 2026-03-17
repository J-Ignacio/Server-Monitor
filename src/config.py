"""
Centralized Configuration Module for the NOC Monitoring System.

This module manages the configuration settings for the centralized server, remote agents,
and the monitoring dashboard. It loads configuration parameters from a JSON file,
applies default values for missing keys, and ensures forward compatibility with newer
configuration schemas.

Attributes:
    SISTEMA_OPERATIVO (str): The detected operating system.
    BASE_DIR (Path): The root directory of the application.
    CONFIG_DIR (Path): The directory storing configuration files.
    CONFIG_FILE (Path): The absolute path to the main configuration file (`config.json`).
    DATA_DIR (Path): The directory for application data storage.
    DB_FILE (Path): The absolute path to the SQLite database file.
    CONFIGURACION_PREDETERMINADA (dict): The default configuration schema and values.
"""

import os
import json
import sys
from pathlib import Path

SISTEMA_OPERATIVO = "Windows"

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

CONFIG_DIR.mkdir(exist_ok=True)

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_FILE = DATA_DIR / "metricas.db"

CONFIGURACION_PREDETERMINADA = {
    "servidor_central": {
        "ip": "192.168.4.99",
        "puerto": 8000,
        "host": "0.0.0.0"
    },
    "agente": {
        "intervalo_envio": 5,
        "timeout": 5,
        "reintentos": 3,
        "espera_reintento": 5,
        "ip_manual": ""
    },
    "dashboard": {
        "intervalo_actualizacion": 2,
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

def _fusionar_configs(cargada: dict, predeterminada: dict) -> bool:
    """
    Recursively merges default configuration parameters into the loaded configuration.

    This function adds missing keys from `predeterminada` into `cargada` without
    overwriting existing values.

    Args:
        cargada (dict): The configuration dictionary loaded from the file.
        predeterminada (dict): The default configuration dictionary schema.

    Returns:
        bool: True if `cargada` was modified during the merge operation, False otherwise.
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

def cargar_config() -> dict:
    """
    Loads configuration settings from the JSON file.

    If the configuration file does not exist, it creates one using the default schema.
    If the file is corrupted, it renames the corrupted file and applies the default schema.
    It also ensures that any missing keys in the loaded configuration are updated based
    on the default schema.

    Returns:
        dict: A dictionary containing the final configuration settings.
    """
    config_cargada = CONFIGURACION_PREDETERMINADA.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_leida = json.load(f)
            if _fusionar_configs(config_leida, CONFIGURACION_PREDETERMINADA):
                guardar_config(config_leida)
            return config_leida
        except json.JSONDecodeError as e:
            print(f"[Error] The configuration file '{CONFIG_FILE}' is corrupted: {e}")
            mal_config_path = CONFIG_FILE.with_suffix('.json.bad')
            try:
                CONFIG_FILE.rename(mal_config_path)
                print(f"  -> Renamed corrupted file to '{mal_config_path.name}'")
            except OSError as rename_error:
                print(f"  -> Failed to rename corrupted file: {rename_error}")
            print("  -> Falling back to default configuration.")
            guardar_config(config_cargada)
            return config_cargada
        except Exception as e:
            print(f"[Warning] Unexpected error loading configuration: {e}")
            print("  -> Falling back to default configuration.")
            return config_cargada
    else:
        guardar_config(CONFIGURACION_PREDETERMINADA)
        return config_cargada

def guardar_config(config: dict) -> None:
    """
    Saves the provided configuration dictionary to the JSON file.

    Args:
        config (dict): The configuration dictionary to be serialized and saved.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Error] Failed to save configuration: {e}")

CONFIG = cargar_config()

if "email" not in CONFIG:
    CONFIG["email"] = CONFIGURACION_PREDETERMINADA["email"]
    guardar_config(CONFIG)

SERVIDOR_CENTRAL_IP = CONFIG["servidor_central"]["ip"]
SERVIDOR_CENTRAL_PUERTO = CONFIG["servidor_central"]["puerto"]
SERVIDOR_CENTRAL_HOST = CONFIG["servidor_central"]["host"]

AGENTE_INTERVALO = CONFIG["agente"]["intervalo_envio"]
AGENTE_TIMEOUT = CONFIG["agente"]["timeout"]
AGENTE_REINTENTOS = CONFIG["agente"]["reintentos"]
AGENTE_ESPERA_REINTENTO = CONFIG["agente"]["espera_reintento"]
AGENTE_IP_MANUAL = CONFIG["agente"].get("ip_manual", "")

DASHBOARD_INTERVALO = CONFIG["dashboard"]["intervalo_actualizacion"]
DASHBOARD_HOST = CONFIG["dashboard"]["host"]
DASHBOARD_PUERTO = CONFIG["dashboard"]["puerto"]

DEBUG = CONFIG["sistema"]["debug"]
LOGS_HABILITADOS = CONFIG["sistema"]["logs_habilitados"]
ARCHIVO_LOG = CONFIG["sistema"]["archivo_log"]

EMAIL_CONFIG = CONFIG["email"]

SEGURIDAD = CONFIG.get("seguridad", CONFIGURACION_PREDETERMINADA["seguridad"])
USAR_SSL = SEGURIDAD.get("usar_ssl", False)
SSL_CERT = BASE_DIR / SEGURIDAD.get("archivo_cert", "certs/cert.pem")
SSL_KEY = BASE_DIR / SEGURIDAD.get("archivo_key", "certs/key.pem")
VERIFICAR_SSL = SEGURIDAD.get("verificar_ssl", False)

PROTOCOLO = "https" if USAR_SSL else "http"
URL_REPORTAR = f"{PROTOCOLO}://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/reportar"
URL_ESTADO = f"{PROTOCOLO}://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/estado"

if DEBUG:
    print("[DEBUG] Debug mode enabled.")
    print(f"[System] OS: {SISTEMA_OPERATIVO}")
    print(f"[Config] File path: {CONFIG_FILE}")
