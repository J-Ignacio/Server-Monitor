"""Dashboard web: visualiza métricas en tiempo real usando Streamlit"""
import streamlit as st
import requests
import time
import pandas as pd
import os
import base64
import sys
from pathlib import Path
from datetime import datetime, timezone

# Asegurar que el directorio raíz está en el path para importar src.config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DASHBOARD_INTERVALO, SERVIDOR_CENTRAL_PUERTO, USAR_SSL, VERIFICAR_SSL, BASE_DIR

# Función auxiliar para recargar la página (compatible con versiones antiguas)
def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# Configurar página
st.set_page_config(page_title="NOC Monitor", layout="wide")

def obtener_datos():
    """Obtiene métricas del servidor central"""
    try:
        # Usamos 127.0.0.1 (localhost) para asegurar que el dashboard siempre encuentre a la API
        # independientemente de la IP de la red o si cambiamos de PC.
        protocolo = "https" if USAR_SSL else "http"
        response = requests.get(f"{protocolo}://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/estado", timeout=2, verify=VERIFICAR_SSL)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        st.warning(f"⚠️  No se puede conectar a la API local (Puerto {SERVIDOR_CENTRAL_PUERTO})")
        return {}

# --- Configuración de Tema (Sidebar) ---
with st.sidebar:
    # Logo de la empresa (busca logo.png en la carpeta raíz)
    logo_path = BASE_DIR / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_column_width=True)
    
    # --- Botón de Exportación ---
    st.write("---")
    if st.button("📥 Descargar Reporte CSV"):
        try:
            protocolo = "https" if USAR_SSL else "http"
            # Usamos el endpoint de estado para obtener la lista, pero idealmente sería un endpoint de dump
            # Por simplicidad, convertimos los datos actuales a CSV
            df_export = pd.DataFrame(obtener_datos().values())
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Guardar CSV", csv, "reporte_noc.csv", "text/csv")
        except Exception as e:
            st.error(f"Error al generar reporte: {e}")
            
    st.header("⚙️ Configuración")
    tema_oscuro = st.toggle("Modo Oscuro", value=True)

# Inyectar CSS dinámico según el estado del toggle
if tema_oscuro:
    custom_css = """
    <style>
        /* Ocultar barra superior de Streamlit (Deploy, Menu, Running, etc) */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

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
        /* Botones: Asegurar legibilidad en modo oscuro */
        .stButton > button {
            color: #ffffff !important;
            background-color: #262730 !important;
            border: 1px solid #4c4c4c !important;
        }
        .stButton > button:hover {
            background-color: #404040 !important;
            border-color: #ffffff !important;
        }
    </style>
    """
else:
    custom_css = """
    <style>
        /* Ocultar barra superior de Streamlit (Deploy, Menu, Running, etc) */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

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

# --- Lógica Principal (Sin bucle infinito) ---
base_datos = obtener_datos()
modo_interaccion = False # Flag para pausar recarga si hay menús abiertos

# Helper para callbacks de estado (evita problemas con rerun manual)
def actualizar_estado(key, valor):
    st.session_state[key] = valor

def enviar_orden(servidor):
    try:
        protocolo = "https" if USAR_SSL else "http"
        requests.post(f"{protocolo}://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/admin/reiniciar/{servidor}", verify=VERIFICAR_SSL)
        st.session_state[f"msg_exito_{servidor}"] = "Orden enviada."
    except Exception as e:
        st.session_state[f"msg_error_{servidor}"] = f"Error: {e}"
    st.session_state[f"conf_{servidor}"] = False

if base_datos:
    # Ordenar servidores alfabéticamente para mantener posición fija
    items_ordenados = sorted(base_datos.items())

    # Crear columnas dinámicas por servidor
    cols = st.columns(len(items_ordenados))
        
    alerta_critica = False

    for i, (servidor, info) in enumerate(items_ordenados):
        # Verificar umbral de alerta (> 90%)
        if info['cpu'] > 90:
            alerta_critica = True

        # --- Cálculo de Estado (Online/Offline) ---
        timestamp_str = info.get('timestamp', '')
        estado_icono = "❓"
        tiempo_atras = "Desconocido"
        
        if timestamp_str:
            try:
                last_seen = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # Usar timezone.utc y quitar info de zona para comparar con fecha naive de SQLite
                diff = (datetime.now(timezone.utc).replace(tzinfo=None) - last_seen).total_seconds()
                tiempo_atras = f"hace {int(diff)}s"
                estado_icono = "🟢" if diff < 30 else ("🟡" if diff < 60 else "🔴")
            except ValueError:
                pass

        with cols[i]:
            with st.expander(f"{estado_icono} {servidor}", expanded=True):
                st.metric(label="CPU", value=f"{info['cpu']}%")
                st.progress(min(info['cpu']/100, 1.0))
            
                st.metric(label="Memoria RAM", value=f"{info['ram']}%")
                st.progress(min(info['ram']/100, 1.0))

                disk = info.get('disk') or 0.0
                st.metric(label="Disco Principal", value=f"{disk}%")
                st.progress(min(disk/100, 1.0))

                temp = info.get('temp') or 0.0
                if temp > 0:
                    st.metric(label="Temperatura", value=f"{temp:.1f} °C")
                    st.progress(min(temp/100, 1.0))
                else:
                    st.metric(label="Temperatura", value="N/A")
                
                st.caption(f"Estado: {tiempo_atras} ({timestamp_str} UTC)")
                
                # Mostrar mensajes flash (éxito/error)
                if f"msg_exito_{servidor}" in st.session_state:
                    st.success(st.session_state.pop(f"msg_exito_{servidor}"))
                if f"msg_error_{servidor}" in st.session_state:
                    st.error(st.session_state.pop(f"msg_error_{servidor}"))

                # --- Botón de Reinicio con Confirmación ---
                # Usamos un contenedor vacío para asegurar que los botones se reemplacen limpiamente
                contenedor_botones = st.empty()
                
                if f"conf_{servidor}" not in st.session_state:
                    st.session_state[f"conf_{servidor}"] = False

                with contenedor_botones.container():
                    if not st.session_state[f"conf_{servidor}"]:
                        st.button("🔄 Reiniciar Servidor", key=f"btn_ask_{servidor}", on_click=actualizar_estado, args=(f"conf_{servidor}", True))
                    else:
                        modo_interaccion = True # Usuario decidiendo, pausar refresh
                        st.warning("¿Estás seguro?")
                        col_si, col_no = st.columns(2)
                        with col_si:
                            st.button("✅ Sí", key=f"btn_yes_{servidor}", on_click=enviar_orden, args=(servidor,))
                        with col_no:
                            st.button("❌ No", key=f"btn_no_{servidor}", on_click=actualizar_estado, args=(f"conf_{servidor}", False))

                # --- Gráfico Histórico ---
                try:
                    protocolo = "https" if USAR_SSL else "http"
                    url_hist = f"{protocolo}://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/historial/{servidor}"
                    resp = requests.get(url_hist, timeout=1, verify=VERIFICAR_SSL)
                    if resp.status_code == 200:
                        datos_hist = resp.json()
                        if datos_hist:
                            df = pd.DataFrame(datos_hist)
                            # Convertir timestamp a fecha/hora para el eje X
                            df["timestamp"] = pd.to_datetime(df["timestamp"])
                            
                            # Definir columnas a graficar dinámicamente (solo si existen)
                            cols_grafico = ["cpu", "ram"]
                            if "temp" in df.columns:
                                cols_grafico.append("temp")
                            if "disk" in df.columns:
                                cols_grafico.append("disk")

                            # Graficar CPU y RAM para ver la tendencia de la última hora
                            st.line_chart(df.set_index("timestamp")[cols_grafico], height=200)
                except requests.exceptions.RequestException:
                    # Si falla la petición (timeout, error de red), muestra este mensaje.
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

# Recarga automática de la página
if not locals().get("modo_interaccion", False):
    time.sleep(DASHBOARD_INTERVALO)
    rerun()