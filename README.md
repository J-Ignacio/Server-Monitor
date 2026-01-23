# 🖥️ Sistema de Monitoreo de Servidores NOC

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
pip install -r requeriments.txt

# Terminal 1: Iniciar API
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# Terminal 2: Iniciar Dashboard
streamlit run src/dashboard.py
```

### Servidor Remoto
```bash
# 1. Copiar AGENTE_FINAL.exe (o agente.py) al servidor
# 2. Doble clic en AGENTE_FINAL.exe
# 3. Editar archivo .bat si necesitas cambiar IP_CENTRAL
```

## 📁 Archivos

| Archivo | Descripción |
|---------|-------------|
| **setup.bat** | Configuración inicial (primera vez) |
| **Iniciar_NOC.bat** | Ejecutar central (API + Dashboard) |
| **AGENTE_FINAL.exe** | Ejecutable para servidores remotos |
| `src/agente.py` | Código fuente del agente |
| `src/servidor.py` | Código fuente del API |
| `src/dashboard.py` | Código fuente del dashboard |
| `config/config.json` | Configuración del sistema |
| `test_configuracion.py` | Script de prueba de configuración |
| `logs/` | Registros del sistema |

## 📚 Documentación

- [📖 Instalación Completa](./docs/instalacion.md)
- [⚙️ Componentes Técnicos](./docs/COMPONENTES.md)
- [🏗️ Arquitectura del Sistema](./docs/arquitectura.md)
- [📤 Compartir a Otra PC](./docs/COMPARTIR_PROYECTO.md)

## ⚙️ Requisitos

- Python 3.8+ (se descarga automáticamente con setup.bat)
- Puerto 8000 disponible (central)
- Red local accesible entre máquinas