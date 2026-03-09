# Technical Documentation: Central API Server `(servidor.py)`

The central server functions as the meeting point for the entire ecosystem. Its responsibility is twofold: to receive data from the agents through a secure endpoint and to serve that same data to the Dashboard for visualization.

## 🛠️ Detailed Analysis by Modules

### 1. Definition of Models and Data Schema
To ensure the data received is correct, we use Pydantic, which automatically validates the data type of each metric.

```python
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import SERVIDOR_CENTRAL_HOST, SERVIDOR_CENTRAL_PUERTO, DEBUG, DB_FILE

app = FastAPI()

# Validation model: Ensures data integrity
class Metricas(BaseModel):
    id_servidor: str   # Agent name and IP
    cpu: float         # Percentage numeric value
    ram: float         # Percentage numeric value
    temp: float        # Temperature in Celsius
    disk: float        # % Disk usage (Primary Partition)
```

- **Automatic Validation:** If an agent accidentally sends text instead of a number in `cpu`, FastAPI will reject the request with a `422 Unprocessable Entity` error before it reaches the database.

- **Decoupling:** Using `DB_FILE` from the centralized configuration allows moving the database to other disks or paths without touching this code.

### 2. Persistence and Database Management

SQLite is ideal for this project because of its lightweight nature and because it does not require an independent database server.

```python
def init_db():
    """Initializes the metrics table if it doesn't exist in the .db file"""
    conn = sqlite3.connect(str(DB_FILE))
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metricas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_servidor TEXT,
            cpu REAL,
            ram REAL,
            temp REAL
        )
    ''')
    
    # Migration: Check if 'temp' column exists and add it if missing
    cursor.execute("PRAGMA table_info(metricas)")
    columnas = [info[1] for info in cursor.fetchall()]
    if "temp" not in columnas:
        print("🔧 Migrating database: Adding 'temp' column...")
        cursor.execute("ALTER TABLE metricas ADD COLUMN temp REAL")

    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"🚀 Monitoring System - Central Server")
```

- `CURRENT_TIMESTAMP`: The database automatically assigns the date and time to each record, ensuring chronological accuracy for dashboard charts.

- `@app.on_event("startup")`: This function runs only once when the server starts, ensuring the table is ready before receiving the first metric.

### 3. Query Endpoints `(GET)`

These routes allow the Dashboard to obtain current and historical information on monitored equipment.

```python
@app.get("/estado")
async def obtener_estado():
    """Returns the last known metric of each registered server"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row # Allows accessing by column name
    cursor = conn.cursor()
    
    # Subquery to get only the last ID for each server
    cursor.execute('''
        SELECT id_servidor, cpu, ram, temp, timestamp 
        FROM metricas 
        WHERE id IN (SELECT MAX(id) FROM metricas GROUP BY id_servidor)
    ''')
    rows = cursor.fetchall()
    conn.close()
    return {row["id_servidor"]: dict(row) for row in rows}

@app.get("/historial/{id_servidor}")
async def obtener_historial(id_servidor: str):
    """Returns the last 50 records of a specific server"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT cpu, ram, timestamp FROM metricas 
        WHERE id_servidor = ? 
        ORDER BY id DESC LIMIT 50
    ''', (id_servidor,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows][::-1] # Inversion for chronological order
```

- **Query Optimization:** The query in `/estado` uses a `GROUP BY` with `MAX(id)` to avoid sending old data to the main panel.

- **Slicing `[::-1]`:** Used to reverse the history list, so the chart in the Dashboard is drawn from left (oldest) to right (most recent).

### 4. Reception Endpoint `(POST)`

This is the gateway for remote agents.

```python
@app.post("/reportar")
async def reportar_metricas(metricas: Metricas):
    """Saves metrics sent by the agent to the database"""
    try:
        conn = sqlite3.connect(str(DB_FILE))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO metricas (id_servidor, cpu, ram, temp) VALUES (?, ?, ?, ?)",
                        (metricas.id_servidor, metricas.cpu, metricas.ram, metricas.temp))
        conn.commit()
        conn.close()
        return {"mensaje": "Métricas guardadas"}
    except Exception as e:
        if DEBUG: print(f"Error BD: {e}")
        raise HTTPException(status_code=500, detail="Error saving metrics")
```

- **SQL Injection:** Using `?` in the `INSERT` statement prevents SQL injection attacks, a good security practice even in internal systems.

- **Exception Handling:** If the database is locked or there is a write error, an `HTTPException 500` is thrown, informing the agent that the data was not saved.

### 5. Server Execution
```python
if __name__ == "__main__":
    import uvicorn
    # Starts the server using the host and port defined in config.py
    uvicorn.run(app, host=SERVIDOR_CENTRAL_HOST, port=SERVIDOR_CENTRAL_PUERTO)
```

- **Uvicorn:** It is the high-performance ASGI server that allows FastAPI to handle multiple requests from agents asynchronously.

### 6. Alert System and Heartbeat Monitoring

The server runs a background task that checks if agents are still "alive".

```python
async def monitor_latidos():
    """Background task: checks if servers have stopped reporting"""
    while True:
        await asyncio.sleep(60) # Check every 60 seconds
        # ... database query logic ...
        
        if delta > 300: # 5 minutes without signal
            if not alertas_activas.get(srv, False):
                print(f"⚠️ ALERT: {srv} has not responded for {int(delta)}s")
                await loop.run_in_executor(None, enviar_correo, f"🚨 ALERT: {srv} Down", ...)
                alertas_activas[srv] = True
```

- **Heartbeat Monitor:** An asynchronous task (`monitor_latidos`) runs in the main loop. It compares the timestamp of the last report with the current time. If the difference is > 300 seconds (5 min), it triggers an email alert.
- **Command Queue:** The `/admin/reiniciar` endpoint saves the command in a `comandos_pendientes` dictionary. When the agent makes its next POST to `/reportar`, the server checks if there are commands for it and delivers them in the JSON response.