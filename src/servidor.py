"""API FastAPI: recibe y almacena métricas de agentes remotos"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Modelo de validación para métricas
class Metricas(BaseModel):
    id_servidor: str   # Identificador del servidor
    cpu: float         # % de uso de CPU
    ram: float         # % de memoria RAM
    temp: float        # Temperatura

# Almacenamiento en memoria (última medición de cada servidor)
base_datos = {}

# GET: Retorna el estado actual de todos los servidores
@app.get("/estado")
async def obtener_estado():
    """Retorna métricas de todos los servidores monitoreados"""
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