# Componentes Técnicos y Ejecutables

## Ejecutables

### `Iniciar_NOC.bat` (Servidor Central)
**Script de lanzamiento automatizado para el sistema de monitoreo central.**

Funcionalidad:
1. Inicializa el servicio FastAPI en el puerto 8000.
2. Implementa un retraso de 3 segundos para la disponibilidad del servicio.
3. Lanza el Dashboard de Streamlit.

Uso:
```powershell
# Ejecutar mediante doble clic o línea de comandos
.\Iniciar_NOC.bat
```

---

### `NOC_SERVICIO.exe` (Agente Remoto)
**Ejecutable de servicio compilado para monitoreo remoto.**

Generado utilizando PyInstaller desde `src/agente_servicio.py`. Desplegado mediante `instalar_agente.bat`.

Uso:
```powershell
# Ejecutar script de instalación como Administrador
.\instalar_agente.bat
```

**Para regenerar el ejecutable:**
```powershell
# Ejecutar herramienta de compilación
.\herramientas.bat
# Seleccionar la Opción [1]
```

---

## Componentes del Código Fuente

### 1. Agente Remoto (`src/agente.py`)
**Implementado en servidores remotos (a través de `AGENTE_FINAL.exe` o código fuente).**

Responsabilidades Principales:
- Recolecta métricas de CPU, RAM y Disco (Partición Principal) en intervalos de 5 segundos.
- Transmite cargas útiles JSON al Servidor Central.
- Implementa lógica de reintento automatizada para fallas de red transitorias.
- **Gestión Remota:** Procesa los comandos de reinicio enviados por el Servidor Central.
- **Sensores de Hardware:** Se integra con WMI/Open Hardware Monitor para obtener métricas térmicas.

Análisis de Configuración:
- **Detección Dinámica de IP:** Resuelve automáticamente su dirección IP local al iniciarse.
- **Enrutamiento Central:** Lee `SERVIDOR_CENTRAL_IP` desde `src/config.py` (o `config.json`).

Ejemplo de Salida:
```
[Info] Agente iniciado exitosamente: SERVER01 (192.168.1.100)
[Info] Endpoint de reporte: http://192.168.1.100:8000/reportar
[Success] Datos transmitidos - CPU: 45.2% | RAM: 62.1% | Disk: 55.4%
```

---

### 2. Servidor API Central (`src/servidor.py`)
**Servicio FastAPI alojado en la infraestructura NOC.**

Endpoints REST:
| Método | Ruta | Descripción |
|--------|-------|-------------|
| GET | `/estado` | Recupera el arreglo de métricas más reciente para todos los nodos registrados. |
| GET | `/historial/{id}` | Recupera los datos históricos de series temporales (últimos 50 puntos de datos). |
| POST | `/reportar` | Endpoint de ingesta para las cargas útiles de los agentes remotos. |
| POST | `/admin/reiniciar/{id}` | Pone en cola una instrucción de reinicio para un nodo de agente específico. |

**GET /estado - Estructura de Respuesta:**
```json
{
  "SERVER01 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "disk": 55.4,
    "temp": 42.0
  }
}
```

**POST /reportar - Estructura de Carga Útil:**
```json
{
  "id_servidor": "SERVER01 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1,
  "temp": 42.0,
  "disk": 55.4
}
```

Puerto Predeterminado: `8000`

---

### 3. Dashboard de Monitoreo (`src/dashboard.py`)
**Interfaz de visualización basada en Streamlit.**

Características:
- Renderiza dinámicamente tarjetas de nodos para todos los servidores registrados.
- Utiliza barras de progreso para la visualización del uso de recursos.
- **Análisis Histórico:** Gráficos de líneas que representan el uso de CPU a lo largo del tiempo.
- **Controles Administrativos:** Mecanismo de reinicio integrado con un modal de confirmación.
- Configurado para actualizaciones asíncronas cada 2 segundos.

Puerto Predeterminado: `8501`

---

## Arquitectura de Comunicación

```text
[NODO REMOTO]             [SERVIDOR CENTRAL]         [CLIENTE WEB]
   Agente                     FastAPI                  Dashboard
  .exe/.py                  servidor.py               dashboard.py
      |                          |                         |
      |--- POST /reportar ------>|                         |
      |   (intervalo 5s)         |                         |
      |                  Persiste en BD                    |
      |                          |                         |
      |                          |<----- GET /estado ------|
      |                          |                         |
      |                          |------- JSON ----------->|
      |<--- Respuesta 200 OK ----|     (intervalo 2s)      |
```

---

## Parámetros de Configuración Globales

Los parámetros están centralizados en `config/config.json`.

### Configuración del Agente
- `intervalo_envio`: Frecuencia de transmisión de métricas (Predeterminado: 5s).
- `timeout`: Umbral de tiempo de espera de la solicitud de red.

### Configuración del Servidor
- `ip`: Enlace de dirección IPv4 del servidor central.
- `puerto`: Puerto de escucha de la API (Predeterminado: 8000).

### Configuración de Seguridad/Sistema
- `usar_ssl`: Alterna el cumplimiento del protocolo HTTPS.
- `logs_habilitados`: Habilita la generación de archivos de registro rotativos.
