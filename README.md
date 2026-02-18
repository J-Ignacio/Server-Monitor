# 🏠 Inicio - Sistema de Monitoreo NOC

Monitoreo en tiempo real de CPU, RAM de múltiples servidores en red local.

## 🚀 Inicio Rápido

### Primera Vez (Setup Inicial)
```bash
# Doble clic en: setup.bat
# Esto crea el ambiente virtual e instala todo automáticamente
```

### Central (Laptop NOC)
**Opción 1: Ejecutable (Recomendado)**
```bash
# Doble clic en: Iniciar_NOC.bat
# Abre automáticamente el API y Dashboard
```

**Opción 2: Manual (Desarrollo)**
```bash
pip install -r requirements.txt

# Terminal 1: Iniciar API
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# Terminal 2: Iniciar Dashboard
streamlit run src/dashboard.py
```

### Servidor Remoto
```bash
# 1. Generar ejecutables usando herramientas.bat (Opción 1)
# 2. Ir a carpeta dist/ y copiar todo el contenido al servidor
# 3. Ejecutar instalar_agente.bat como Administrador
# 4. Editar config/config.json con la IP del servidor central
```

## 📁 Archivos

| Archivo | Descripción |
|---------|-------------|
| **setup.bat** | Configuración inicial (primera vez) |
| **limpiar.bat** | Borra venv y temporales (Factory Reset) |
| **Iniciar_NOC.bat** | Ejecutar central (API + Dashboard) |
| **AGENTE_FINAL.exe** | Ejecutable para servidores remotos |
| `src/agente.py` | Código fuente del agente |
| `src/servidor.py` | Código fuente del API |
| `src/dashboard.py` | Código fuente del dashboard |
| `config/config.json` | Configuración del sistema |
| `test_configuracion.py` | Script de prueba de configuración |
| `logs/` | Registros del sistema |

## 📚 Documentación

- [📖 Guía de Instalación Paso a Paso](./docs/instalacion.md)
- [⚙️ Componentes Técnicos y Ejecutables](./docs/COMPONENTES.md)
- [🏗️ Arquitectura y Flujo de Datos](./docs/arquitectura.md)
- [📘 Guía de Despliegue y Solución de Problemas](./docs/COMPARTIR_PROYECTO.md)

## ⚙️ Requisitos

- Python 3.8+ (se descarga automáticamente con setup.bat)
- Puerto 8000 disponible (central)
- Red local accesible entre máquinas