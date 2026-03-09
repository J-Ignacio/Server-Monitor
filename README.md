# Sistema de Monitoreo NOC

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-00a393.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Un sistema de monitoreo y telemetría centralizado en tiempo real diseñado para Centros de Operaciones de Red (NOC). Esta arquitectura permite el seguimiento continuo del uso de CPU, RAM, Disco y las temperaturas del hardware a través de múltiples servidores distribuidos dentro de una red de área local (LAN) o una red privada virtual (VPN).

## 🚀 Resumen de Arquitectura del Sistema

El sistema opera bajo un modelo cliente-servidor que consta de tres componentes principales:

1. **Agente Remoto (`agente.py` / `AGENTE_FINAL.exe`):** Un demonio ligero implementado en los servidores objetivo. Consulta de forma autónoma los sensores de hardware y transmite cargas útiles JSON al servidor central.
2. **Servidor API Central (`servidor.py`):** Una API REST de alto rendimiento construida con FastAPI. Ingiere la telemetría de los agentes, valida las cargas útiles y persiste los datos de series temporales en una base de datos SQLite.
3. **Dashboard de Monitoreo (`dashboard.py`):** Una interfaz de Streamlit dinámica y asíncrona que consulta la API Central para renderizar visualizaciones en tiempo real y gráficos históricos.

---

## ⚡ Inicio Rápido

### Configuración Inicial del Entorno (Servidor Central)

Para inicializar el entorno de desarrollo y compilar los ejecutables necesarios, ejecute el script de inicio proporcionado:

```bat
:: Haga doble clic en el siguiente script para crear el entorno virtual,
:: instalar dependencias y compilar los artefactos de PyInstaller.
.\setup.bat
```

### Lanzamiento de la Aplicación NOC

**Lanzamiento Automatizado (Recomendado):**
```bat
:: Haga doble clic para iniciar de forma concurrente el servidor FastAPI y el Dashboard de Streamlit.
.\Iniciar_NOC.bat
```

**Ejecución Manual (Desarrollo):**
```powershell
# Asegúrese de que el entorno virtual esté activo
.\venv\Scripts\activate

# Terminal 1: Inicialice el servicio FastAPI
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# Terminal 2: Inicialice el Dashboard de Streamlit
streamlit run src/dashboard.py
```

### Implementación del Agente Remoto

1. Genere los ejecutables independientes utilizando `herramientas.bat` (Opción 1).
2. Navegue al directorio `dist/` y transfiera `AGENTE_PORTABLE.exe` e `instalar_agente.bat` al servidor remoto objetivo.
3. Ejecute `instalar_agente.bat` con **privilegios de Administrador** en el servidor remoto.
4. Actualice `config/config.json` en el servidor remoto para especificar la dirección IP del Servidor Central.
5. Reinicie el agente.

---

## 📁 Estructura del Repositorio

| Recurso | Descripción |
|----------|-------------|
| **`setup.bat`** | Script de inicialización del entorno y resolución de dependencias. |
| **`limpiar.bat`** | Script de desmontaje del entorno (elimina `venv` y artefactos de compilación temporales). |
| **`Iniciar_NOC.bat`** | Script de lanzamiento unificado para los servicios de API y Dashboard. |
| `src/agente.py` | Código fuente para el agente de telemetría remoto. |
| `src/servidor.py` | Código fuente para el servidor central FastAPI. |
| `src/dashboard.py` | Código fuente para la interfaz de visualización de Streamlit. |
| `config/config.json` | Archivo de configuración centralizado (generado automáticamente). |
| `test_configuracion.py` | Script de diagnóstico para validar la configuración del entorno. |
| `logs/` | Directorio que contiene registros de la aplicación en rotación. |

---

## 📚 Documentación Técnica

La documentación completa que detalla las estrategias de implementación, la arquitectura del sistema y los parámetros de configuración está disponible en el directorio `/docs`:

- [Guía de Instalación](./docs/instalacion.md)
- [Arquitectura del Sistema y Flujo de Datos](./docs/arquitectura.md)
- [Especificaciones de Componentes](./docs/COMPONENTES.md)
- [Protocolos de Distribución](./docs/COMPARTIR_PROYECTO.md)
- [Hoja de Referencia Rápida](./docs/REFERENCIA_RAPIDA.md)
- [Registro de Cambios](./docs/CAMBIOS_REALIZADOS.md)

---

## ⚙️ Requisitos del Sistema

- **Tiempo de ejecución:** Python 3.8 o superior.
- **Red:** El puerto 8000 TCP debe ser accesible en el Servidor Central.
- **Conectividad:** Enrutamiento de red confiable entre los Agentes Remotos y el Servidor Central.
- **Métricas de Hardware (Windows):** Para un sondeo térmico preciso en entornos Windows, [OpenHardwareMonitor](https://openhardwaremonitor.org/) debe ejecutarse con privilegios de Administrador.