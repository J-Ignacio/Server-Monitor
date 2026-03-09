# Technical Documentation: Centralized Configuration `(config.py)`

This module manages the persistence of system settings in a JSON file. Its goal is to allow changes to the behavior of the agent, the server, or the dashboard without the need to modify the source code.

## 🛠️ Detailed Analysis by Modules

### 1. Environment Detection and Paths
The code detects whether it is running as a Python script (`.py`) or as a compiled executable (`.exe`), adjusting the base paths so that configuration files are always created in the correct location.

```python
import os
import json
import sys
from pathlib import Path

# Configuration file paths
if getattr(sys, 'frozen', False):
    # If we are running as .exe (PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # If we are running as a normal .py script
    BASE_DIR = Path(__file__).parent.parent

CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_DIR.mkdir(exist_ok=True)
```

- `sys.frozen`: This is the flag used by PyInstaller. If it is `True`, we use the executable's path; if not, the source file's path.
- `pathlib`: Used to handle paths agnostically to the operating system (Windows/Linux).

### 2. Default Configuration
A dictionary with default values is defined. This dictionary serves as a template to create the `config.json` file if it does not exist, or to repair missing keys.

```python
CONFIGURACION_PREDETERMINADA = {
    "servidor_central": {
        "ip": "192.168.4.100",
        "puerto": 8000,
        "host": "0.0.0.0"
    },
    "agente": {
        "intervalo_envio": 5,
        "timeout": 5,
        "reintentos": 3,
        "espera_reintento": 5
    },
    # ... (other settings for dashboard, system, email, security)
}
```

- **Centralization:** All "magic numbers" (ports, timeouts) are located here, rather than scattered throughout the code.

### 3. Recursive Merge Logic
This function is critical for updates. It allows new configuration options to be added in future versions of the software without overwriting the custom settings that the user already has.

```python
def _fusionar_configs(cargada, predeterminada):
    """
    Recursively merges the default configuration into the loaded one,
    adding only the missing keys without overwriting existing ones.
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
```

- **Recursiveness:** Allows navigating within sub-sections (e.g., `servidor_central` -> `ip`) to check for nested keys.

### 4. Loading and Auto-repair
The system attempts to load the JSON. If it fails (corrupt file), it renames it and creates a new one to ensure the service never stops due to a configuration error.

```python
def cargar_config():
    config_cargada = CONFIGURACION_PREDETERMINADA.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_leida = json.load(f)
            # Update missing keys
            if _fusionar_configs(config_leida, CONFIGURACION_PREDETERMINADA):
                guardar_config(config_leida)
            return config_leida
        except json.JSONDecodeError as e:
            print(f"❌ Error: Corrupt configuration. Renaming...")
            CONFIG_FILE.rename(CONFIG_FILE.with_suffix('.json.bad'))
            guardar_config(config_cargada)
            return config_cargada
    else:
        guardar_config(CONFIGURACION_PREDETERMINADA)
        return config_cargada
```

- **Resilience:** The system prioritizes availability ("keep running") over strict correctness, regenerating the configuration if necessary.

### 5. Exporting Variables
Finally, the module exposes the variables in uppercase so they can be easily imported by `agente.py`, `servidor.py`, and `dashboard.py`.

```python
CONFIG = cargar_config()

SERVIDOR_CENTRAL_IP = CONFIG["servidor_central"]["ip"]
SERVIDOR_CENTRAL_PUERTO = CONFIG["servidor_central"]["puerto"]
# ...
USAR_SSL = CONFIG["seguridad"]["usar_ssl"]
URL_REPORTAR = f"{'https' if USAR_SSL else 'http'}://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/reportar"
```

## 2. Technical Explanation

### Path Management and Compatibility
This section is critical. The code detects whether it is running as a script (`.py`) or as a frozen executable (`.exe` with PyInstaller) using `sys.frozen`. This ensures that the `config` and `data` folders are always created next to the executable, avoiding "Path not found" errors.

### Loading and Saving
The functions `cargar_config` and `guardar_config` handle JSON persistence.
- **Auto-repair:** If the JSON file is corrupt, the system renames it to `.bad` and creates a new one with default values so it does not stop.
- **Configuration Merging:** If you update the software and there are new configuration options, the `_fusionar_configs` function adds them to your existing file without deleting your previous settings.

### Global Variables
The script exports uppercase variables (e.g., `SERVIDOR_CENTRAL_IP`) so other modules can easily import them. It also dynamically builds the URLs (`URL_REPORTAR`) based on whether SSL is active or not.