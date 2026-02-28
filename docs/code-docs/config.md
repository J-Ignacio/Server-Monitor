# Documentación Técnica: Configuración Centralizada `(config.py)`

Este módulo gestiona la persistencia de los ajustes del sistema en un archivo JSON. Su objetivo es permitir cambios en el comportamiento del agente, el servidor o el dashboard sin necesidad de modificar el código fuente.

## 🛠️ Análisis Detallado por Módulos

### 1. Detección de Entorno y Rutas
El código detecta si se está ejecutando como un script de Python (`.py`) o como un ejecutable compilado (`.exe`), ajustando las rutas base para que los archivos de configuración siempre se creen en el lugar correcto.

```python
import os
import json
import sys
from pathlib import Path

# Rutas de archivos de configuración
if getattr(sys, 'frozen', False):
    # Si estamos ejecutando como .exe (PyInstaller)
    BASE_DIR = Path(sys.executable).parent
else:
    # Si estamos ejecutando como script .py normal
    BASE_DIR = Path(__file__).parent.parent

CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_DIR.mkdir(exist_ok=True)
```

- `sys.frozen`: Es la bandera que usa PyInstaller. Si es `True`, usamos la ruta del ejecutable; si no, la del archivo fuente.
- `pathlib`: Se usa para manejar rutas de forma agnóstica al sistema operativo (Windows/Linux).

### 2. Configuración Predeterminada
Se define un diccionario con los valores por defecto. Este diccionario sirve como plantilla para crear el archivo `config.json` si no existe, o para reparar claves faltantes.

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
    # ... (otros ajustes de dashboard, sistema, email, seguridad)
}
```

- **Centralización:** Todos los "números mágicos" (puertos, tiempos de espera) están aquí, no dispersos en el código.

### 3. Lógica de Fusión (Merge) Recursiva
Esta función es crítica para las actualizaciones. Permite agregar nuevas opciones de configuración en versiones futuras del software sin sobrescribir los ajustes personalizados que el usuario ya tenga.

```python
def _fusionar_configs(cargada, predeterminada):
    """
    Fusiona recursivamente la configuración predeterminada en la cargada,
    añadiendo solo las claves que falten sin sobreescribir las existentes.
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

- **Recursividad:** Permite navegar dentro de las sub-secciones (ej: `servidor_central` -> `ip`) para verificar claves anidadas.

### 4. Carga y Auto-reparación
El sistema intenta cargar el JSON. Si falla (archivo corrupto), lo renombra y crea uno nuevo para asegurar que el servicio nunca se detenga por un error de configuración.

```python
def cargar_config():
    config_cargada = CONFIGURACION_PREDETERMINADA.copy()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_leida = json.load(f)
            # Actualizar claves faltantes
            if _fusionar_configs(config_leida, CONFIGURACION_PREDETERMINADA):
                guardar_config(config_leida)
            return config_leida
        except json.JSONDecodeError as e:
            print(f"❌ Error: Configuración corrupta. Renombrando...")
            CONFIG_FILE.rename(CONFIG_FILE.with_suffix('.json.bad'))
            guardar_config(config_cargada)
            return config_cargada
    else:
        guardar_config(CONFIGURACION_PREDETERMINADA)
        return config_cargada
```

- **Resiliencia:** El sistema prioriza la disponibilidad ("seguir funcionando") sobre la corrección estricta, regenerando la configuración si es necesario.

### 5. Exportación de Variables
Finalmente, el módulo expone las variables en mayúsculas para que sean importadas fácilmente por `agente.py`, `servidor.py` y `dashboard.py`.

```python
CONFIG = cargar_config()

SERVIDOR_CENTRAL_IP = CONFIG["servidor_central"]["ip"]
SERVIDOR_CENTRAL_PUERTO = CONFIG["servidor_central"]["puerto"]
# ...
USAR_SSL = CONFIG["seguridad"]["usar_ssl"]
URL_REPORTAR = f"{'https' if USAR_SSL else 'http'}://{SERVIDOR_CENTRAL_IP}:{SERVIDOR_CENTRAL_PUERTO}/reportar"
```

## 2. Explicación Técnica

### Gestión de Rutas y Compatibilidad
Esta sección es crítica. El código detecta si está corriendo como script (`.py`) o como ejecutable congelado (`.exe` con PyInstaller) usando `sys.frozen`. Esto asegura que las carpetas `config` y `data` se creen siempre junto al ejecutable, evitando errores de "Ruta no encontrada".

### Carga y Guardado
Las funciones `cargar_config` y `guardar_config` manejan la persistencia en JSON.
- **Auto-reparación:** Si el archivo JSON está corrupto, el sistema lo renombra a `.bad` y crea uno nuevo con los valores por defecto para no detenerse.
- **Fusión de Configuración:** Si actualizas el software y hay nuevas opciones de configuración, la función `_fusionar_configs` las agrega a tu archivo existente sin borrar tus ajustes previos.

### Variables Globales
El script exporta variables en mayúsculas (ej. `SERVIDOR_CENTRAL_IP`) para que otros módulos las importen fácilmente. También construye dinámicamente las URLs (`URL_REPORTAR`) basándose en si SSL está activo o no.