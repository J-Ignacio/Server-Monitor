"""API FastAPI: recibe y almacena métricas de agentes remotos"""
import sqlite3
import asyncio
import smtplib
from email.message import EmailMessage
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import SERVIDOR_CENTRAL_HOST, SERVIDOR_CENTRAL_PUERTO, DEBUG, DB_FILE, EMAIL_CONFIG, USAR_SSL, SSL_CERT, SSL_KEY

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

# --- Sistema de Alertas (Heartbeat) ---
alertas_activas = {} # Cache para no repetir alertas: { "id_servidor": True/False }

def enviar_correo(asunto, cuerpo):
    """Envía un correo electrónico usando la configuración SMTP"""
    if not EMAIL_CONFIG["habilitado"]: return

    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg["Subject"] = asunto
    msg["From"] = EMAIL_CONFIG["usuario"]
    msg["To"] = EMAIL_CONFIG["destinatario"]

    try:
        server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CONFIG["usuario"], EMAIL_CONFIG["password"])
        server.send_message(msg)
        server.quit()
        print(f"📧 Alerta enviada a {EMAIL_CONFIG['destinatario']}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

async def monitor_latidos():
    """Tarea en segundo plano: verifica si los servidores han dejado de reportar"""
    print("👀 Iniciando monitor de latidos (Heartbeat)...")
    while True:
        await asyncio.sleep(60) # Verificar cada 60 segundos
        try:
            conn = sqlite3.connect(str(DB_FILE))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Obtener la última fecha de reporte de cada servidor
            cursor.execute('SELECT id_servidor, MAX(timestamp) as ultimo FROM metricas GROUP BY id_servidor')
            rows = cursor.fetchall()
            conn.close()

            ahora = datetime.utcnow()
            for row in rows:
                srv = row["id_servidor"]
                ultimo = datetime.strptime(row["ultimo"], "%Y-%m-%d %H:%M:%S")
                delta = (ahora - ultimo).total_seconds()

                if delta > 300: # 5 minutos sin señal
                    if not alertas_activas.get(srv, False):
                        print(f"⚠️ ALERTA: {srv} no responde hace {int(delta)}s")
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None, enviar_correo, f"🚨 ALERTA: {srv} Caído", f"El servidor {srv} dejó de reportar hace más de 5 minutos.\nÚltimo reporte: {row['ultimo']} UTC")
                        alertas_activas[srv] = True
                else:
                    if alertas_activas.get(srv, False):
                        print(f"✅ RECUPERADO: {srv}")
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(None, enviar_correo, f"✅ RECUPERADO: {srv}", f"El servidor {srv} ha vuelto a reportar.")
                        alertas_activas[srv] = False
        except Exception as e:
            print(f"Error en monitor: {e}")

# Evento de inicio: Muestra información en la consola al arrancar con uvicorn
@app.on_event("startup")
async def startup_event():
    init_db()
    asyncio.create_task(monitor_latidos())
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
    # Obtenemos registros de la última hora, con un límite para seguridad.
    # El agente envía cada ~5s, 1 hora = ~720 registros. Limitamos a 1000.
    cursor.execute('''
        SELECT cpu, ram, timestamp FROM (
            SELECT cpu, ram, timestamp 
            FROM metricas 
            WHERE id_servidor = ? 
              AND timestamp >= datetime('now', '-1 hour', 'utc')
            ORDER BY timestamp DESC
            LIMIT 1000
        ) 
        ORDER BY timestamp ASC;
    ''', (id_servidor,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    
    if USAR_SSL:
        if DEBUG: print(f"🔒 Iniciando servidor seguro (HTTPS)")
        if not SSL_CERT.exists() or not SSL_KEY.exists():
            print(f"❌ Error: No se encuentran los certificados en: {SSL_CERT.parent}")
            exit(1)
            
        uvicorn.run(app, host=SERVIDOR_CENTRAL_HOST, port=SERVIDOR_CENTRAL_PUERTO, 
                    ssl_keyfile=str(SSL_KEY), 
                    ssl_certfile=str(SSL_CERT))
    else:
        uvicorn.run(app, host=SERVIDOR_CENTRAL_HOST, port=SERVIDOR_CENTRAL_PUERTO)