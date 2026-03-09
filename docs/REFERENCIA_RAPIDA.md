# Guía de Referencia Rápida

## Ejecución Principal

### Inicialización del Servidor Central
```powershell
# Haga doble clic o ejecute:
.\Iniciar_NOC.bat
```
*Inicializa el servicio FastAPI y el Dashboard de Streamlit simultáneamente.*

### Inicialización del Agente Remoto
```powershell
# Haga doble clic o ejecute:
.\AGENTE_PORTABLE.exe
```
*Inicializa la recolección y transmisión de métricas. Requiere configuración previa de la IP en `config.json`.*

---

## Endpoints Críticos

| Recurso | URL | Descripción |
|----------|-----|-------------|
| **Dashboard** | `http://localhost:8501` | Interfaz principal de visualización. |
| **Estado API** | `http://localhost:8000/estado` | Endpoint GET que devuelve el arreglo de nodos actual (JSON). |
| **Documentación API** | `http://localhost:8000/docs` | Interfaz de Swagger detallando los endpoints REST. |

---

## Estructuras de Datos

**Formato de Respuesta de GET `/estado`:**
```json
{
  "SERVER01 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 42.0,
    "disk": 55.4
  },
  "SERVER02 (192.168.1.101)": {
    "cpu": 28.5,
    "ram": 41.3,
    "temp": 38.5,
    "disk": 80.1
  }
}
```

---

## Anulación de Parámetros de Configuración

Para anular manualmente el enrutamiento del Servidor Central en un nodo de agente, edite el archivo `config/config.json` generado:

```json
{
  "servidor_central": {
    "ip": "192.168.4.143",
    "puerto": 8000
  }
}
```

---

## Resoluciones de Diagnóstico Comunes

| Síntoma | Causa Probable | Acción Correctiva |
|---------|----------------|-------------------|
| Dashboard Vacío | Agentes incapaces de establecer conexión. | Valide la IP de `servidor_central` en `config.json` del agente. |
| "Puerto 8000 en uso" | Proceso API fantasma ocupando el puerto. | Termine los procesos `python.exe` o reinicie el Servidor Central. |
| Tiempo de Espera | Tráfico de entrada bloqueado por el firewall del sistema operativo. | Ejecute regla `allow` del firewall para el puerto TCP 8000. |

---

## Flujo de Trabajo para Desarrolladores

```powershell
# 1. Inicializar Entorno de Python
python -m venv venv
.\venv\Scripts\activate

# 2. Resolver Dependencias
pip install -r requirements.txt

# 3. Generar Artefactos
.\herramientas.bat
```
