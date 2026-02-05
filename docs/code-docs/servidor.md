# Documentación Técnica: Servidor Central API `(servidor.py)`

El servidor central funciona como el punto de encuentro de todo el ecosistema. Su responsabilidad es doble: recibir datos de los agentes mediante un endpoint seguro y servir esos mismos datos al Dashboard para su visualización.

## 🛠️ Análisis Detallado por Módulos

### 1. Definición de Modelos y Esquema de Datos
Para garantizar que los datos recibidos sean correctos, utilizamos Pydantic, que valida automáticamente el tipo de dato de cada métrica.

```
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import SERVIDOR_CENTRAL_HOST, SERVIDOR_CENTRAL_PUERTO, DEBUG, DB_FILE

app = FastAPI()

# Modelo de validación: Asegura integridad de datos
class Metricas(BaseModel):
    id_servidor: str   # Nombre e IP del agente
    cpu: float         # Valor numérico porcentual
    ram: float         # Valor numérico porcentual
    temp: float        # Temperatura en Celsius
```

- Validación Automática: Si un agente envía accidentalmente un texto en lugar de un número en `cpu`, FastAPI rechazará la petición con un error `422 Unprocessable Entity` antes de que llegue a la base de datos.

- Desacoplamiento: El uso de `DB_FILE` desde la configuración centralizada permite mover la base de datos a otros discos o rutas sin tocar este código.

### 2. Persistencia y Gestión de Base de Datos

SQLite es ideal para este proyecto por su ligereza y porque no requiere un servidor de base de datos independiente.

```
def init_db():
    """Inicializa la tabla de métricas si no existe en el archivo .db"""
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

@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"🚀 Sistema de Monitoreo - Servidor Central")
```

- `CURRENT_TIMESTAMP`: La base de datos asigna automáticamente la fecha y hora a cada registro, lo que garantiza precisión cronológica para los gráficos del dashboard.

- `@app.on_event("startup")`: Esta función se ejecuta solo una vez al encender el servidor, asegurando que la tabla esté lista antes de recibir la primera métrica.

### 3. Endpoints de Consulta `(GET)`

Estas rutas permiten al Dashboard obtener la información actual e histórica de los equipos monitoreados.

```
@app.get("/estado")
async def obtener_estado():
    """Retorna la última métrica conocida de cada servidor registrado"""
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row # Permite acceder por nombre de columna
    cursor = conn.cursor()
    
    # Subconsulta para obtener solo el último ID por cada servidor
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
    """Retorna los últimos 50 registros de un servidor específico"""
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
    return [dict(row) for row in rows][::-1] # Inversión para orden cronológico
```

- Optimización de Consulta: La consulta en `/estado` utiliza un `GROUP BY` con `MAX(id)` para evitar enviar datos viejos al panel principal.

- Slicing `[::-1]`: Se usa para invertir la lista del historial, de modo que el gráfico en el Dashboard se dibuje de izquierda (más antiguo) a derecha (más reciente).

### 4. Endpoint de Recepción `(POST)`

Es la puerta de entrada para los agentes remotos.

```
@app.post("/reportar")
async def reportar_metricas(metricas: Metricas):
    """Guarda en la base de datos las métricas enviadas por el agente"""
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
        raise HTTPException(status_code=500, detail="Error al guardar métricas")
```

- Inyección SQL: El uso de `?` en la sentencia `INSERT` previene ataques de inyección SQL, una buena práctica de seguridad incluso en sistemas internos.

- Manejo de Excepciones: Si la base de datos está bloqueada o hay un error de escritura, se lanza una `HTTPException 500`, informando al agente que el dato no se guardó.

### 5. Ejecución del Servidor
```
if __name__ == "__main__":
    import uvicorn
    # Inicia el servidor usando el host y puerto definidos en config.py
    uvicorn.run(app, host=SERVIDOR_CENTRAL_HOST, port=SERVIDOR_CENTRAL_PUERTO)
```

- Uvicorn: Es el servidor ASGI de alto rendimiento que permite que FastAPI maneje múltiples peticiones de agentes de forma asíncrona.