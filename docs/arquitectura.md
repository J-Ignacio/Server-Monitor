# 🏗️ Arquitectura

## Diagrama de Flujo

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│ SERVIDOR REMOTO  │         │ SERVIDOR CENTRAL │         │  NAVEGADOR WEB   │
│   (Agente)       │         │    (FastAPI)     │         │   (Dashboard)    │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         │                            │                            │
         │ POST /reportar             │                            │
         │ {cpu, ram, temp}           │                            │
         ├───────────────────────────>│                            │
         │                       Almacena                          │
         │                            │                            │
         │                            │<───── GET /estado ─────────│
         │                            │                            │
         │                            ├──────JSON────────────────>│
         │ (cada 5 seg)               │        (actualiza c/2s)   │
         │                            │                            │
         ├───────────────────────────>│                            │
```

## Componentes

### 1. Agente Remoto (`agente.py`)
- Corre en cada servidor remoto
- Recopila: CPU, RAM cada 5 segundos
- Envía JSON al endpoint POST `/reportar`
- Reintentos automáticos en desconexión

### 2. Servidor Central (`servidor.py`)
- API FastAPI en laptop central
- Dos endpoints:
  - `POST /reportar`: recibe métricas (válida con Pydantic)
  - `GET /estado`: retorna dict con última medición
- Almacenamiento: diccionario en memoria
- Puerto: 8000

### 3. Dashboard (`dashboard.py`)
- Interfaz Streamlit
- Actualiza cada 2 segundos
- Layout dinámico (columnas por servidor)
- Barras de progreso visuales

## Protocolo de Comunicación

### Request (Agente → Servidor)
```http
POST /reportar HTTP/1.1
Host: 192.168.4.143:8000
Content-Type: application/json

{
  "id_servidor": "SERVIDOR1 (192.168.1.100)",
  "cpu": 45.2,
  "ram": 62.1,
  "temp": 0.0
}
```

### Response (Servidor → Agente)
```json
{
  "status": "ok"
}
```

### Request (Dashboard → Servidor)
```http
GET /estado HTTP/1.1
Host: localhost:8000
```

### Response (Servidor → Dashboard)
```json
{
  "SERVIDOR1 (192.168.1.100)": {
    "cpu": 45.2,
    "ram": 62.1,
    "temp": 0.0
  }
}
```

## Seguridad

- ⚠️ Sin autenticación (asume red corporativa segura)
- ⚠️ HTTP solo (no HTTPS, solo LAN)
- Para producción agregar:
  - HTTPS/SSL
  - Token authentication
  - Validación de origen

## Limitaciones

- **Almacenamiento**: En memoria (se pierden datos al reiniciar)
- **Temperatura**: No disponible (necesita drivers específicos)
- **Escala**: ~100 servidores máximo
- **Persistencia**: Implementar base de datos si se requiere histórico

## Despliegue (RDP)

1. Conectar por RDP al servidor remoto
2. Copiar `agente.py` con Ctrl+C/V
3. Instalar: `pip install requests psutil`
4. Editar IP_CENTRAL con IP de laptop central
5. Ejecutar: `python agente.py`