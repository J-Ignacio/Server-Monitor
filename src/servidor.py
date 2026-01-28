"""API FastAPI: recibe y almacena métricas de agentes remotos"""
from fastapi import FastAPI
from pydantic import BaseModel
from src.config import SERVIDOR_CENTRAL_HOST, SERVIDOR_CENTRAL_PUERTO, DEBUG

app = FastAPI()

# Modelo de validación para métricas
class Metricas(BaseModel):
    id_servidor: str   # Identificador del servidor
    cpu: float         # % de uso de CPU
    ram: float         # % de memoria RAM
    temp: float        # Temperatura

# Almacenamiento en memoria (última medición de cada servidor)
base_datos = {}

# Evento de inicio: Muestra información en la consola al arrancar con uvicorn
@app.on_event("startup")
async def startup_event():
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
    if DEBUG:
        print(f"📊 Solicitud de estado - Total servidores: {len(base_datos)}")
    return base_datos

# POST: Recibe y guarda métricas de un agente
@app.post("/reportar")
def recibir_metricas(datos: Metricas):
    """Almacena métricas enviadas por un agente"""
    base_datos[datos.id_servidor] = {
        "cpu": datos.cpu,
        "ram": datos.ram,
        "temp": datos.temp
    }
    print(f"✅ [{datos.id_servidor}] CPU: {datos.cpu}% | RAM: {datos.ram}%")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVIDOR_CENTRAL_HOST, port=SERVIDOR_CENTRAL_PUERTO)