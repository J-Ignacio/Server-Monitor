"""Dashboard web: visualiza métricas en tiempo real usando Streamlit"""
import streamlit as st
import requests
import time
import pandas as pd
import os
import base64
import sys
import re
from pathlib import Path
from datetime import datetime, timezone
import sqlite3
import json
 
# Asegurar que el directorio raíz está en el path para importar src.config
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DASHBOARD_INTERVALO, SERVIDOR_CENTRAL_PUERTO, USAR_SSL, VERIFICAR_SSL, BASE_DIR, DB_FILE

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

    st.write("---")
    st.subheader("🕒 Sincronización")
    offset_manual = st.number_input("Ajuste de Horas", min_value=-24, max_value=24, value=0, step=1, help="Usa esto si los servidores salen Offline por diferencia de horario.")
    
    st.write("---")
    st.subheader("⚙️ Preferencias")
    # Control de frecuencia de actualización
    frecuencia_refresh = st.slider("Velocidad de Actualización (s)", min_value=1, max_value=30, value=2, help="Tiempo de espera entre recargas.")
    modo_compacto = st.toggle("Vista Compacta", value=False, help="Oculta barras de progreso para ahorrar espacio.")

    # --- Zona de Peligro (Borrado Masivo) ---
    st.write("---")
    with st.expander("⚠️ Zona de Peligro"):
        if st.button("🔥 Borrar TODOS los servidores", help="Elimina todo el historial y servidores de la base de datos."):
            try:
                conn = sqlite3.connect(str(DB_FILE))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM metricas")
                conn.commit()
                conn.close()
                st.success("Base de datos vaciada.")
                time.sleep(1)
                rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.write("---")
    st.caption("v2.0 - Diseño NOC Profesional")

# --- CSS Estilo Glassmorphism / Dark NOC ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap');

    /* Reset y fondo global */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #1a1a2e 0%, #050505 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Ocultar elementos de Streamlit no deseados */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Estilo de la Tarjeta del Servidor */
    .server-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 10px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .server-card:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: rgba(0, 255, 157, 0.4);
        box-shadow: 0 15px 40px 0 rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 255, 157, 0.1);
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Modo Compacto */
    .server-card.compact .progress-track { display: none; }
    .server-card.compact .metric-box { padding: 5px 10px; }
    .server-card.compact .metric-value { font-size: 1rem; }
    .server-card.compact { padding: 15px; }

    /* Header de la tarjeta */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 12px;
    }
    
    .server-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Indicador de Estado (Punto brillante) */
    .status-indicator {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        position: relative;
    }
    
    .status-indicator::after {
        content: '';
        position: absolute;
        top: -4px; left: -4px; right: -4px; bottom: -4px;
        border-radius: 50%;
        opacity: 0.4;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.4; }
        70% { transform: scale(1.5); opacity: 0; }
        100% { transform: scale(1); opacity: 0; }
    }
    
    .status-online { background-color: #00ff9d; box-shadow: 0 0 10px #00ff9d; }
    .status-online::after { background-color: #00ff9d; }
    
    .status-warning { background-color: #ffcc00; box-shadow: 0 0 10px #ffcc00; }
    .status-warning::after { background-color: #ffcc00; }
    
    .status-offline { background-color: #ff4d4d; box-shadow: 0 0 10px #ff4d4d; }
    .status-offline::after { background-color: #ff4d4d; }

    /* Grid de Métricas */
    .metrics-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
    }
    
    .metric-box {
        background: rgba(0, 0, 0, 0.2);
        padding: 12px;
        border-radius: 8px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #888;
        margin-bottom: 6px;
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.2rem;
        font-weight: 700;
        color: #fff;
    }
    
    .metric-unit {
        font-size: 0.8rem;
        color: #666;
    }

    /* Barras de Progreso Custom */
    .progress-track {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        margin-top: 8px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.5s ease;
        position: relative;
        overflow: hidden;
    }

    /* Efecto de brillo animado (Shimmer) */
    .progress-fill::after {
        content: "";
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%);
        transform: translateX(-100%);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        100% { transform: translateX(100%); }
    }

    /* Footer de la tarjeta */
    .card-footer {
        margin-top: 15px;
        font-size: 0.75rem;
        color: #555;
        text-align: right;
    }

    /* Ajustes para componentes nativos de Streamlit */
    .stButton > button {
        width: 100%;
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #fff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: #fff !important;
    }
    
    /* Expander transparente */
    [data-testid="stExpander"] {
        background-color: transparent !important;
        border: none !important;
    }
    [data-testid="stExpander"] summary {
        color: #888 !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #fff !important;
    }

    /* --- NUEVO: Estilos para el HUD (Panel Superior) --- */
    .hud-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-bottom: 30px;
    }
    .hud-card {
        flex: 1;
        min-width: 140px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    .hud-card:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .hud-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    .hud-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #aaa;
        margin-top: 5px;
    }
    
    /* Título con Gradiente */
    .noc-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00ff9d 0%, #00b8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        text-shadow: 0 0 30px rgba(0, 255, 157, 0.2);
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Reemplazamos el título estándar por uno HTML con gradiente
st.markdown('<div class="noc-title">🖥️ NOC MONITOR</div>', unsafe_allow_html=True)

# Contenedor que se actualiza dinámicamente
placeholder = st.empty()

# --- Lógica Principal (Sin bucle infinito) ---
base_datos = obtener_datos()
modo_interaccion = False # Flag para pausar recarga si hay menús abiertos

# Mostrar estado de conexión en Sidebar
with st.sidebar:
    if base_datos:
        st.success(f"✅ API Conectada ({len(base_datos)} equipos)")
    else:
        st.error("❌ API Desconectada")

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

# Helper para colores de barras (Definido fuera del bucle para optimizar)
def get_color(val):
    if val < 60: return "#00ff9d" # Verde neón
    if val < 85: return "#ffcc00" # Amarillo
    return "#ff4d4d" # Rojo

if base_datos:
    # Ordenar servidores alfabéticamente para mantener posición fija
    items_ordenados = sorted(base_datos.items())

    # --- PRE-CALCULO DE ESTADISTICAS (Para evitar parpadeo del HUD) ---
    stats_total = len(items_ordenados)
    stats_online = 0
    stats_offline = 0

    for _, info in items_ordenados:
        timestamp_str = info.get('timestamp', '')
        
        # Valores por defecto para la UI
        info['_status_class'] = "status-offline"
        info['_status_text'] = "OFFLINE"
        info['_tiempo_atras'] = "Desconocido"
        is_online = False
        
        if timestamp_str:
            try:
                if "." in timestamp_str:
                    last_seen = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    last_seen = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                now_utc = datetime.utcnow()
                now_local = datetime.now()
                diff_utc = (now_utc - last_seen).total_seconds()
                diff_local = (now_local - last_seen).total_seconds()
                diff = diff_utc if abs(diff_utc) < abs(diff_local) else diff_local
                diff -= (offset_manual * 3600)
                if diff < 0: diff = 0
                
                # Formato amigable de tiempo
                if diff < 60: info['_tiempo_atras'] = f"hace {int(diff)}s"
                elif diff < 3600: info['_tiempo_atras'] = f"hace {int(diff/60)}m"
                elif diff < 86400: info['_tiempo_atras'] = f"hace {int(diff/3600)}h"
                else: info['_tiempo_atras'] = f"hace {int(diff/3600)}h ({last_seen.strftime('%H:%M')})"

                if diff < 45:
                    info['_status_class'] = "status-online"
                    info['_status_text'] = "ONLINE"
                    is_online = True
                elif diff < 60:
                    info['_status_class'] = "status-warning"
                    info['_status_text'] = "LENTO"
                    is_online = True
            except:
                info['_tiempo_atras'] = "Error fecha"
        
        if is_online:
            stats_online += 1
        else:
            stats_offline += 1

    # --- Renderizar HUD (Panel Superior) ---
    hud_html = f"""
    <div class="hud-container">
        <div class="hud-card">
            <div class="hud-value">{stats_total}</div>
            <div class="hud-label">Total Servidores</div>
        </div>
        <div class="hud-card" style="border-bottom: 3px solid #00ff9d;">
            <div class="hud-value" style="color: #00ff9d;">{stats_online}</div>
            <div class="hud-label">Online</div>
        </div>
        <div class="hud-card" style="border-bottom: 3px solid #ff4d4d;">
            <div class="hud-value" style="color: #ff4d4d;">{stats_offline}</div>
            <div class="hud-label">Offline</div>
        </div>
    </div>
    """
    st.markdown(hud_html, unsafe_allow_html=True)

    # --- Tabla de Administración de Agentes ---
    st.markdown("### 📋 Administración de Agentes")

    # Crear cabecera de la tabla
    col_nombre, col_estado, col_conexion, col_accion = st.columns([3, 1, 2, 1])
    with col_nombre: st.markdown("**Nombre del Servidor**")
    with col_estado: st.markdown("**Estado**")
    with col_conexion: st.markdown("**Última Conexión**")
    with col_accion: st.markdown("**Acciones**")

    st.markdown("---")

    for i, (servidor, info) in enumerate(items_ordenados):
        col_nombre, col_estado, col_conexion, col_accion = st.columns([3, 1, 2, 1])

        # Parseo del Nombre del Servidor
        servidor_display = servidor
        match = re.match(r"(.* \()([0-9a-fA-F:\.\- ]+)(\))", servidor)
        if match:
            hostname_part = match.group(1)
            ips_part = match.group(2)
            end_part = match.group(3)
            primera_ip = ips_part.split(" - ")[0].strip()
            servidor_display = f"{hostname_part}{primera_ip}{end_part}"

        with col_nombre:
            st.write(servidor_display)

        with col_estado:
            # Lógica de Estado (5 minutos)
            # El cálculo se hizo en el pre-cálculo y se guardó en `_status_class` y `_status_text`
            is_online = info.get('_status_class') in ['status-online', 'status-warning']
            estado_icon = "🟢" if is_online else "🔴"
            st.write(f"{estado_icon} {'Online' if is_online else 'Offline'}")

        with col_conexion:
            timestamp_str = info.get('timestamp', 'Desconocido')
            if timestamp_str != 'Desconocido':
                try:
                    # Mostrar la fecha exacta y el tiempo transcurrido
                    if "." in timestamp_str:
                        last_seen = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                    else:
                        last_seen = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    st.write(f"{last_seen.strftime('%Y-%m-%d %H:%M:%S')} ({info.get('_tiempo_atras')})")
                except:
                    st.write(timestamp_str)
            else:
                st.write("Desconocido")

        with col_accion:
            if st.button("🗑️", key=f"btn_del_table_{servidor}", help="Eliminar Agente"):
                try:
                    conn = sqlite3.connect(str(DB_FILE))
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM metricas WHERE id_servidor = ?", (servidor,))
                    conn.commit()
                    conn.close()
                    st.success(f"Eliminado: {servidor}")
                    time.sleep(1)
                    rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📊 Vistas de Métricas")

    # --- Lógica de Grid (Cuadrícula) ---
    # En lugar de una columna por servidor, usamos filas de 3 columnas
    COLUMNAS_POR_FILA = 3
    filas = [items_ordenados[i:i + COLUMNAS_POR_FILA] for i in range(0, len(items_ordenados), COLUMNAS_POR_FILA)]
        
    alerta_critica = False

    # Iteramos por filas para crear el grid
    for fila in filas:
        cols = st.columns(COLUMNAS_POR_FILA)
        
        for i, (servidor, info) in enumerate(fila):
        # Verificar umbral de alerta (> 90%)
            if info['cpu'] > 90:
                alerta_critica = True

            # --- Lectura de Estado Pre-calculado ---
            status_class = info.get('_status_class', 'status-offline')
            status_text = info.get('_status_text', 'OFFLINE')
            tiempo_atras = info.get('_tiempo_atras', 'Desconocido')

            cpu_color = get_color(info['cpu'])
            ram_color = get_color(info['ram'])
            disk_color = get_color(info.get('disk', 0))
            temp_val = info.get('temp', 0)
            temp_color = get_color(temp_val if temp_val > 0 else 0)

            # Clase extra para modo compacto
            css_compacto = "compact" if modo_compacto else ""

            # --- Parseo del Nombre del Servidor para mostrar solo una IP ---
            servidor_display = servidor
            # Buscamos un formato como "Hostname (192.168.1.5 - 10.0.0.2)"
            match = re.match(r"(.* \()([0-9a-fA-F:\.\- ]+)(\))", servidor)
            if match:
                hostname_part = match.group(1)
                ips_part = match.group(2)
                end_part = match.group(3)
                # Tomamos la primera IP antes de cualquier " - "
                primera_ip = ips_part.split(" - ")[0].strip()
                servidor_display = f"{hostname_part}{primera_ip}{end_part}"

            # --- Construcción de Tarjeta HTML ---
            raw_html = f"""
            <div class="server-card {css_compacto}">
                <div class="card-header">
                    <div class="server-title">
                        <span class="status-indicator {status_class}"></span>
                        {servidor_display}
                    </div>
                    <div style="font-size: 0.8rem; color: #666;">{status_text}</div>
                </div>
                
                <div class="metrics-container">
                    <div class="metric-box">
                        <div class="metric-label">CPU</div>
                        <div class="metric-value">{info['cpu']}<span class="metric-unit">%</span></div>
                        <div class="progress-track"><div class="progress-fill" style="width: {info['cpu']}%; background-color: {cpu_color};"></div></div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">RAM</div>
                        <div class="metric-value">{info['ram']}<span class="metric-unit">%</span></div>
                        <div class="progress-track"><div class="progress-fill" style="width: {info['ram']}%; background-color: {ram_color};"></div></div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">DISCO</div>
                        <div class="metric-value">{info.get('disk', 0)}<span class="metric-unit">%</span></div>
                        <div class="progress-track"><div class="progress-fill" style="width: {info.get('disk', 0)}%; background-color: {disk_color};"></div></div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">TEMP</div>
                        <div class="metric-value">{info.get('temp', 'N/A')}<span class="metric-unit">°C</span></div>
                        <div class="progress-track"><div class="progress-fill" style="width: {min(temp_val, 100)}%; background-color: {temp_color};"></div></div>
                    </div>
                </div>
                <div class="card-footer">Última conexión: {tiempo_atras}</div>
            </div>
            """
            # Limpieza agresiva: eliminamos saltos de línea y espacios extra para evitar que Markdown lo detecte como código
            html_card = "".join([line.strip() for line in raw_html.split("\n")])

            with cols[i]:
                # Renderizar tarjeta visual
                st.markdown(html_card, unsafe_allow_html=True)
                
                # Sección de detalles interactivos (oculta por defecto para limpieza)
                with st.expander("📉 Historial y Acciones"):
                    
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

                    # --- Usuarios Conectados ---
                    usuarios_data = info.get("usuarios")
                    if usuarios_data:
                        try:
                            usuarios_lista = json.loads(usuarios_data) if isinstance(usuarios_data, str) else usuarios_data
                            if usuarios_lista:
                                df_usuarios = pd.DataFrame(usuarios_lista)
                                st.markdown("##### 👥 Usuarios Conectados")
                                st.dataframe(df_usuarios, hide_index=True, use_container_width=True)
                            else:
                                st.caption("No hay usuarios conectados detectados.")
                        except Exception as e:
                            st.caption("Error al cargar usuarios.")
                    else:
                        st.caption("No hay datos de usuarios disponibles.")

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

                    # Botón de eliminación movido a la tabla de administración
            
    # --- Trigger de Alerta Global (Audio + Visual) ---
    # Se ejecuta una sola vez al final si algún servidor activó la bandera
    if alerta_critica:
        st.toast("🔥 ¡ALERTA CRÍTICA! CPU > 90% detectado", icon="🔥")
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
    time.sleep(frecuencia_refresh)
    rerun()