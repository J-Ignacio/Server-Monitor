"""Dashboard web: visualiza métricas en tiempo real usando Streamlit"""
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
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        /* Headers, textos y métricas */
        h1, h2, h3, p, .stMarkdown, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #ffffff !important;
        }
        /* Expander: Fondo oscuro para evitar texto invisible sobre fondo blanco por defecto */
        [data-testid="stExpander"] summary {
            color: #ffffff !important;
            background-color: #262730 !important;
        }
        [data-testid="stExpander"] summary:hover {
            background-color: #404040 !important;
        }
        /* Iconos SVG específicos (ej. flecha expander) */
        [data-testid="stExpander"] summary svg {
            fill: #ffffff !important;
        }
        [data-testid="stSidebar"] {
            background-color: #262730;
        }
    </style>
    """
else:
    custom_css = """
    <style>
        .stApp {
            background-color: #ffffff;
            color: #31333f;
        }
        [data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
    </style>
    """

st.markdown(custom_css, unsafe_allow_html=True)

st.title("🖥️ Sistema de Monitoreo NOC")

# Contenedor que se actualiza dinámicamente
placeholder = st.empty()

def obtener_datos():
    """Obtiene métricas del servidor central"""
    try:
        # Usamos 127.0.0.1 (localhost) para asegurar que el dashboard siempre encuentre a la API
        # independientemente de la IP de la red o si cambiamos de PC.
        response = requests.get(f"http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/estado", timeout=2)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        st.warning(f"⚠️  No se puede conectar a la API local (Puerto {SERVIDOR_CENTRAL_PUERTO})")
        return {}

# Bucle de actualización (cada DASHBOARD_INTERVALO segundos)
while True:
    try:
        base_datos = obtener_datos()
        
        with placeholder.container():
            if base_datos:
                # Crear columnas dinámicas por servidor
                cols = st.columns(len(base_datos))
                alerta_critica = False
            
                for i, (servidor, info) in enumerate(base_datos.items()):
                    # Verificar umbral de alerta (> 90%)
                    if info['cpu'] > 90:
                        alerta_critica = True

                    with cols[i]:
                        with st.expander(f"🖥️ {servidor}", expanded=True):
                            st.metric(label="CPU", value=f"{info['cpu']}%")
                            st.progress(min(info['cpu']/100, 1.0))
                        
                            st.metric(label="Memoria RAM", value=f"{info['ram']}%")
                            st.progress(min(info['ram']/100, 1.0))
                        
                            temp = info.get('temp', 0.0)
                            if temp > 0:
                                st.write(f"🌡️ Temperatura: **{temp:.1f} °C**")
                            else:
                                st.write(f"🌡️ Temperatura: N/A")
                                
                            st.caption(f"Última actualización: {time.strftime('%H:%M:%S')}")
                            
                            # --- Gráfico Histórico ---
                            try:
                                url_hist = f"http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/historial/{servidor}"
                                resp = requests.get(url_hist, timeout=1)
                                if resp.status_code == 200:
                                    datos_hist = resp.json()
                                    if datos_hist:
                                        df = pd.DataFrame(datos_hist)
                                        # Convertir timestamp a fecha/hora para el eje X
                                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                                        st.line_chart(df.set_index("timestamp")["cpu"], height=150)
                            except Exception:
                                st.caption("Cargando historial...")
                
                # --- Trigger de Alerta (Audio + Visual) ---
                if alerta_critica:
                    st.error("🔥 ¡ALERTA CRÍTICA! Uso de CPU superior al 90% detectado.")
                    sound_file = "alert.mp3"
                    if os.path.exists(sound_file):
                        try:
                            with open(sound_file, "rb") as f:
                                data = f.read()
                                b64 = base64.b64encode(data).decode()
                                st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                        except Exception:
                            pass
            else:
                st.info("Esperando conexión de agentes remotos...")
    except KeyboardInterrupt:
        st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
    
    time.sleep(DASHBOARD_INTERVALO)