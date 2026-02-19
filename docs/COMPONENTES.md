# 📦 Componentes Técnicos y Ejecutables

## 🚀 Ejecutables

### `Iniciar_NOC.bat` (Central)
**Script que ejecuta el sistema central completo**

Qué hace:
1. Inicia API FastAPI en puerto 8000
2. Espera 3 segundos
3. Inicia Dashboard Streamlit
4. Todo en una sola ejecución

Uso:
```powershell
# Doble clic en Iniciar_NOC.bat
```

---

### `NOC_SERVICIO.exe` (Servidor Remoto)
**Ejecutable compilado del agente como Servicio**

Generado con PyInstaller desde `src/agente_servicio.py`. Se instala usando `instalar_agente.bat`.

Uso:
```powershell
# Ejecutar instalar_agente.bat como Administrador
```

**Para regenerar .exe:**
```powershell
herramientas.bat -> Opción [1]
```

---

## 💻 Componentes de Código

### 1. Agente (`src/agente.py`)
**Se ejecuta en cada servidor remoto (via AGENTE_FINAL.exe)**

Función:
- Recopila CPU, RAM cada 5 segundos
- Envía datos al servidor central
- Reintentos automáticos si hay desconexión
- **Gestión Remota:** Ejecuta comandos de reinicio recibidos del servidor
- **Sensores:** Intenta leer temperatura vía WMI (Windows) o psutil

Configuración:

```python
IP_CENTRAL = "192.168.4.143"  # Cambiar con IP de laptop NOC
```
- **Automática:** Detecta su propia IP al iniciar.
- **Destino:** Lee `src/config.py` (o `config.json` si existe).
- **IP Servidor:** Se define en `CONFIGURACION_PREDETERMINADA["servidor_central"]["ip"]`.

Salida:
```
✓ Agente iniciado: SERVIDOR1 (192.168.1.100)
✓ Reportando a: http://192.168.1.100:8000/reportar
✓ Datos enviados
```

---

### 2. Servidor (`src/servidor.py`)
**API FastAPI que corre en laptop central**

Endpoints:
| Método | Ruta | Función |
|--------|------|---------|
| GET | `/estado` | Retorna métricas de todos los servidores |
| GET | `/historial/{id}` | Retorna historial de métricas (últimos 50) |
| POST | `/reportar` | Recibe métricas de un agente |
| POST | `/admin/reiniciar/{id}` | Encola orden de reinicio para un agente |

**GET /estado - Response:**
```json
{
  "SERVIDOR1 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1
  }
}
```

**POST /reportar - Request:**
```json
{
  "id_servidor": "SERVIDOR1 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1
}
```

Puerto: `8000`

---

### 3. Dashboard (`src/dashboard.py`)
**Interfaz web Streamlit en laptop central**

Características:
- Muestra un recuadro por cada servidor
- Barras de progreso visuales
- **Gráfico histórico:** Línea de tiempo de uso de CPU
- **Botón de Reinicio:** Con confirmación de seguridad
- Actualización cada 2 segundos
- Timestamp de última actualización

Puerto: `8501`

---

## 🔄 Flujo de Comunicación

```
[SERVIDOR REMOTO]         [SERVIDOR CENTRAL]     [NAVEGADOR]
   Agente                     FastAPI             Dashboard
  .exe/.py                    servidor.py         dashboard.py
      |                          |                    |
      |-- POST /reportar ------>|                    |
      |  (cada 5 segundos)      |                    |
      |                    Almacena              
      |                         |
      |                         |<-- GET /estado ---|
      |                         |                    |
      |                      JSON ----->  Renderiza
      |<-- Reconocimiento OK---|
```

---

## 📊 Variables Globales

### Agente
- `IP_CENTRAL`: IP del servidor central
- `PUERTO`: 8000 (default)
- `ID_SERVIDOR`: "hostname (IP.local)"

### Servidor
- `DB_FILE`: Ruta al archivo `data/metricas.db` (SQLite)
- `EMAIL_CONFIG`: Credenciales SMTP para alertas
- `SSL_CERT/KEY`: Rutas para modo HTTPS

### Dashboard
- `placeholder`: Contenedor que se refresca cada 2s
- URL: `http://localhost:8000/estado`
