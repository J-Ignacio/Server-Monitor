from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Definimos que ahora recibiremos 4 datos
class Metricas(BaseModel):
    id_servidor: str
    cpu: float
    ram: float
    temp: float 
base_datos = {}

@app.get("/")
def home():
    return {"datos": base_datos}

@app.post("/reportar")
def recibir_metricas(datos: Metricas):
    base_datos[datos.id_servidor] = {
        "cpu": datos.cpu, 
        "ram": datos.ram,
        "temp": datos.temp
    }
    print(f"✅ [{datos.id_servidor}] -> CPU: {datos.cpu}% | Temp: {datos.temp}°C")
    return {"status": "ok"}