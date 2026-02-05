# Documentación Técnica: Dashboard de Visualización `(dashboard.py)`
El Dashboard es una aplicación web interactiva que consume la API del servidor central para mostrar el estado de todos los agentes conectados en tiempo real.

## 🛠️ Análisis Detallado por Módulos

### 1. Configuración de Interfaz y Estilo Dinámico

Streamlit permite inyectar CSS para personalizar la apariencia. Este bloque gestiona el "Modo Oscuro" y la estructura base de la página.

```
import streamlit as st
import requests
import time
import pandas as pd
import os
import base64
from src.config import DASHBOARD_INTERVALO, SERVIDOR_CENTRAL_PUERTO

# Configurar página
st.set_page_config(page_title="NOC Monitor", layout="wide")

# --- Configuración de Tema (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    tema_oscuro = st.toggle("Modo Oscuro", value=True)

# Inyectar CSS dinámico según el estado del toggle
if tema_oscuro:
    custom_css = """
    <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        h1, h2, h3, p, .stMarkdown, [data-testid="stMetricValue"] { color: #ffffff !important; }
        [data-testid="stExpander"] summary { background-color: #262730 !important; color: #ffffff !important; }
    </style>
    """
else:
    custom_css = "<style>.stApp { background-color: #ffffff; }</style>"

st.markdown(custom_css, unsafe_allow_html=True)
st.title("🖥️ Sistema de Monitoreo NOC")
```

- `st.set_page_config(layout="wide")`: Aprovecha todo el ancho de la pantalla, ideal para visualizar múltiples servidores en columnas.

- Inyección de CSS: Se utiliza `unsafe_allow_html=True` para forzar estilos que Streamlit no permite modificar por defecto, como el color de fondo de los contenedores expandibles.

### 2. Consumo de Datos de la API

El dashboard no lee la base de datos directamente; consulta los endpoints del servidor central.

```
# Contenedor que se actualiza dinámicamente
placeholder = st.empty()

def obtener_datos():
    """Obtiene métricas del servidor central"""
    try:
        # Se apunta a 127.0.0.1 porque el Dashboard suele correr en el mismo host que la API
        response = requests.get(f"http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/estado", timeout=2)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        st.warning(f"⚠️ No se puede conectar a la API local")
        return {}
```

- `st.empty()`: Crea un espacio reservado en la interfaz. Esto permite que el dashboard se "limpie" y se vuelva a dibujar en cada ciclo sin acumular elementos hacia abajo.

- Encapsulamiento: Al usar la API central, el dashboard se mantiene ligero y desacoplado de la lógica de la base de datos.

### 3. Renderizado de Servidores y Gráficos Históricos

Este bloque procesa la lista de servidores y genera columnas dinámicas con métricas y gráficos de rendimiento.

```
# Bucle de actualización constante
while True:
    try:
        base_datos = obtener_datos()
        with placeholder.container():
            if base_datos:
                items_ordenados = sorted(base_datos.items())
                cols = st.columns(len(items_ordenados))
                alerta_critica = False
            
                for i, (servidor, info) in enumerate(items_ordenados):
                    if info['cpu'] > 90: alerta_critica = True

                    with cols[i]:
                        with st.expander(f"🖥️ {servidor}", expanded=True):
                            st.metric(label="CPU", value=f"{info['cpu']}%")
                            st.progress(min(info['cpu']/100, 1.0))
                            
                            # --- Gráfico Histórico ---
                            try:
                                url_hist = f"http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/historial/{servidor}"
                                resp = requests.get(url_hist, timeout=1)
                                if resp.status_code == 200:
                                    df = pd.DataFrame(resp.json())
                                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                                    st.line_chart(df.set_index("timestamp")["cpu"], height=150)
                            except: pass
```

- `st.columns`: Crea una rejilla dinámica. Si hay 3 agentes conectados, se crean 3 columnas automáticamente.

- `st.line_chart`: Utiliza Pandas para procesar el historial y mostrar una gráfica de líneas del uso de CPU. Es crucial convertir el `timestamp` a objeto `datetime` para que el eje X sea cronológico.

### 4. Sistema de Alertas (Visual y Sonora)

Una de las funciones más importantes para un NOC (Network Operations Center) es la notificación inmediata de fallos.

```
                # --- Trigger de Alerta (Audio + Visual) ---
                if alerta_critica:
                    st.error("🔥 ¡ALERTA CRÍTICA! Uso de CPU superior al 90% detectado.")
                    sound_file = "alert.mp3"
                    if os.path.exists(sound_file):
                        try:
                            with open(sound_file, "rb") as f:
                                data = f.read()
                                b64 = base64.b64encode(data).decode()
                                # Inyección de HTML5 para auto-reproducción de audio
                                st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                        except: pass
```                        

- Base64 Audio: Como Streamlit no tiene un componente nativo de "alarma sonora", se lee un archivo MP3 local, se codifica en Base64 y se inyecta una etiqueta de HTML5 `<audio autoplay>`.

- Lógica de Umbral: La variable `alerta_critica` se activa si cualquier servidor del bucle supera el 90% de CPU.

5. Control de Ciclo
```
    except Exception as e:
        st.error(f"Error: {e}")
    
    time.sleep(DASHBOARD_INTERVALO)
```

- `time.sleep`: Controla la tasa de refresco. Un valor típico es 2-5 segundos para evitar sobrecargar el navegador y la API. n