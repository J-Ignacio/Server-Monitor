# 📦 Componentes del Sistema

## 🚀 Ejecutables

### `Iniciar_NOC.bat` (Central)
**Script que ejecuta el sistema central completo**

Qué hace:
1. Inicia API FastAPI en puerto 8000
2. Espera 3 segundos
3. Inicia Dashboard Streamlit
4. Todo en una sola ejecución

Uso:
```bash
# Doble clic en Iniciar_NOC.bat
```

---

### `AGENTE_FINAL.exe` (Servidor Remoto)
**Ejecutable compilado del agente**

Generado con PyInstaller desde `src/agente.py`

Uso:
```bash
# Doble clic en AGENTE_FINAL.exe
# O crear config.bat para configurar IP_CENTRAL
```

**Para regenerar .exe:**
```bash
pyinstaller AGENTE_FINAL.spec
```

---

## 💻 Componentes de Código

### 1. Agente (`src/agente.py`)
**Se ejecuta en cada servidor remoto (via AGENTE_FINAL.exe)**

Función:
- Recopila CPU, RAM cada 5 segundos
- Envía datos al servidor central
- Reintentos automáticos si hay desconexión

Configuración:
```python
IP_CENTRAL = "192.168.4.143"  # Cambiar con IP de laptop NOC
```

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
| POST | `/reportar` | Recibe métricas de un agente |

**GET /estado - Response:**
```json
{
  "SERVIDOR1 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 0.0
  }
}
```

**POST /reportar - Request:**
```json
{
  "id_servidor": "SERVIDOR1 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1,
  "temp": 0.0
}
```

Puerto: `8000`

---

### 3. Dashboard (`src/dashboard.py`)
**Interfaz web Streamlit en laptop central**

Características:
- Muestra un recuadro por cada servidor
- Barras de progreso visuales
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
- `base_datos`: Diccionario {servidor: {cpu, ram, temp}}

### Dashboard
- `placeholder`: Contenedor que se refresca cada 2s
- URL: `http://localhost:8000/estado`
