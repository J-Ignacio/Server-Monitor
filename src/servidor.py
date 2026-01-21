from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Definimos el modelo de datos
class Metricas(BaseModel):
    id_servidor: str
    cpu: float
    ram: float
    temp: float 

# Diccionario donde guardamos la info (Asegúrate de usar el mismo nombre siempre)
base_datos = {}

@app.get("/estado")
async def obtener_estado():
    # CAMBIO AQUÍ: Debe coincidir con el nombre del diccionario arriba
    return base_datos

@app.post("/reportar")
def recibir_metricas(datos: Metricas):
    # Guardamos los datos usando el id del servidor como llave
    base_datos[datos.id_servidor] = {
        "cpu": datos.cpu, 
        "ram": datos.ram,
        "temp": datos.temp
    }
    print(f"✅ [{datos.id_servidor}] -> CPU: {datos.cpu}% | Temp: {datos.temp}°C")
    return {"status": "ok"}