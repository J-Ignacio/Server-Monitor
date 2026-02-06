"""API FastAPI: recibe y almacena métricas de agentes remotos"""
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import SERVIDOR_CENTRAL_HOST, SERVIDOR_CENTRAL_PUERTO, DEBUG, DB_FILE

app = FastAPI()

# Modelo de validación para métricas
class Metricas(BaseModel):
    id_servidor: str   # Identificador del servidor
    cpu: float         # % de uso de CPU
    ram: float         # % de memoria RAM
    temp: float        # Temperatura

# --- Funciones de Base de Datos ---
def init_db():
    """Inicializa la base de datos SQLite si no existe"""
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
    conn.commit()
    conn.close()

# Evento de inicio: Muestra información en la consola al arrancar con uvicorn
@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"\n🚀 Sistema de Monitoreo - Servidor Central")
    print(f"📡 Escuchando en: {SERVIDOR_CENTRAL_HOST}:{SERVIDOR_CENTRAL_PUERTO}")
    print(f"📊 Estado: http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/estado")
    print(f"📄 Docs:   http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/docs\n")

# Ruta raíz para verificar fácilmente si el servidor está vivo
@app.get("/")
def root():
    return {"sistema": "NOC Monitor", "estado": "Online", "versión": "1.0"}

# GET: Retorna el estado actual de todos los servidores
@app.get("/estado")
async def obtener_estado():
    """Retorna métricas de todos los servidores monitoreados"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener la última métrica de cada servidor
    cursor.execute('''
        SELECT id_servidor, cpu, ram, temp, timestamp 
        FROM metricas 
        WHERE id IN (SELECT MAX(id) FROM metricas GROUP BY id_servidor)
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return {row["id_servidor"]: dict(row) for row in rows}

# POST: Recibe métricas de un agente y las guarda en BD
@app.post("/reportar")
async def reportar_metricas(metricas: Metricas):
    try:
        conn = sqlite3.connect(str(DB_FILE))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO metricas (id_servidor, cpu, ram, temp) VALUES (?, ?, ?, ?)",
                       (metricas.id_servidor, metricas.cpu, metricas.ram, metricas.temp))
        conn.commit()
        conn.close()
        print(f"✅ [{metricas.id_servidor}] CPU: {metricas.cpu}% | RAM: {metricas.ram}%")
        return {"mensaje": "Métricas guardadas"}
    except Exception as e:
        if DEBUG: print(f"Error BD: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar métricas")

# GET: Retorna el historial de métricas de un servidor (para gráficos)
@app.get("/historial/{id_servidor}")
async def obtener_historial(id_servidor: str):
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtenemos registros de la última hora
    cursor.execute('''
        SELECT cpu, ram, timestamp FROM metricas 
        WHERE id_servidor = ? 
        AND timestamp >= datetime('now', '-1 hour')
        ORDER BY timestamp ASC
    ''', (id_servidor,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVIDOR_CENTRAL_HOST, port=SERVIDOR_CENTRAL_PUERTO)