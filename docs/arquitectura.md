# Arquitectura y Flujo de Datos

## Diagrama de Flujo del Sistema

```text
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│    NODO REMOTO   │         │ SERVIDOR CENTRAL │         │    CLIENTE WEB   │
│     (Agente)     │         │    (FastAPI)     │         │   (Dashboard)    │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         │ POST /reportar             │                            │
         │ {cpu, ram, disk, temp}     │                            │
         ├───────────────────────────>│                            │
         │                            │                            │
         │                 Persiste en BD (SQLite)                 │
         │                            │                            │
         │                            │<───── GET /estado ─────────│
         │                            │                            │
         │                            ├────── Respuesta JSON ──────>│
         │                            │    (Actualiza cada 2s)     │
         │ (Intervalo de 5s)          │                            │
         ├───────────────────────────>│                            │
```

## Componentes del Sistema

### 1. Agente Remoto (`agente.py`)
- Desplegado en los nodos de infraestructura objetivo.
- **Recolección de Métricas:** Captura la utilización de CPU, RAM, Disco y la Temperatura en intervalos definidos.
- **Transmisión:** Envía cargas útiles JSON al endpoint POST `/reportar`.
- **Resiliencia:** Implementa mecanismos de retroceso exponencial y reintentos para particiones de red.
- **Sensores:** Interroga a WMI/psutil para obtener datos térmicos, condicionado al soporte de hardware y privilegios administrativos.

### 2. Servidor Central (`servidor.py`)
- Aloja una interfaz REST FastAPI en el hardware del NOC centralizado.
- **Endpoints:**
  - `POST /reportar`: Ingiere y valida las cargas útiles de métricas a través de esquemas Pydantic.
  - `GET /estado`: Devuelve las métricas registradas más recientemente para los nodos activos.
  - `GET /historial/{id}`: Devuelve una matriz de series temporales de métricas históricas.
  - `POST /admin/reiniciar/{id}`: Pone en cola una instrucción de reinicio para un nodo de agente específico.
- **Capa de Almacenamiento:** Utiliza SQLite (`data/metricas.db`) para la retención de datos persistente y ligera.
- **Red:** Se vincula al puerto `8000` por defecto.

### 3. Dashboard de Monitoreo (`dashboard.py`)
- Aplicación Streamlit que sirve como la capa principal de visualización.
- Implementa un sondeo asíncrono para actualizar dinámicamente los estados de los nodos.
- Renderiza componentes de interfaz de usuario receptivos, gráficos históricos y controles administrativos.

## Protocolo de Comunicación

### Solicitud Entrante (Agente → Servidor)
```http
POST /reportar HTTP/1.1
Host: 192.168.4.143:8000
Content-Type: application/json

{
  "id_servidor": "SERVER01 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1,
  "temp": 42.0,
  "disk": 55.4
}
```

### Respuesta del Servidor (Servidor → Agente)
```json
{
  "status": "ok",
  "comando": null
}
```

### Consulta de Datos (Dashboard → Servidor)
```http
GET /estado HTTP/1.1
Host: localhost:8000
```

### Respuesta de la Consulta (Servidor → Dashboard)
```json
{
  "SERVER01 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 42.0,
    "disk": 55.4,
    "timestamp": "2023-10-27T10:00:00Z"
  }
}
```

## Consideraciones de Seguridad

- **Autenticación:** Actualmente opera sin autenticación nativa; depende de la seguridad del perímetro de red (VLAN/VPN).
- **Transporte:** Por defecto usa HTTP plano. Las implementaciones de producción sobre redes no confiables requieren habilitar el parámetro de configuración SSL/TLS.
- **Mejoras Futuras:** Se debe implementar autenticación basada en tokens y validación estricta de origen antes de una implementación a gran escala.

## Limitaciones del Sistema

- **Métricas Térmicas:** La dependencia de APIs a nivel de SO (WMI/psutil) o servicios externos (OpenHardwareMonitor) requiere configuraciones de hardware específicas y privilegios elevados.
- **Escalabilidad:** La implementación actual de SQLite está optimizada para entornos que escalan hasta aproximadamente 100 nodos concurrentes. Los entornos que superen este umbral pueden requerir la migración a un RDBMS robusto (ej. PostgreSQL).
