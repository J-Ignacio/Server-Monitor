import streamlit as st
import requests
import time

st.set_page_config(page_title="NOC Monitor", layout="wide")
st.title("🖥️ Sistema de Monitoreo NOC")

# 1. Creamos un contenedor vacío que se refrescará
placeholder = st.empty()

def obtener_datos():
    try:
        # Ajusta la IP si es necesario
        response = requests.get("http://localhost:8000/estado", timeout=2)
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

while True:
    base_datos = obtener_datos()
    
    # 2. Todo lo que pongamos dentro de 'with placeholder.container()' se sobrescribirá
    with placeholder.container():
        if base_datos:
            # Creamos columnas dinámicas según cuántos servidores hay
            cols = st.columns(len(base_datos))
            
            for i, (servidor, info) in enumerate(base_datos.items()):
                with cols[i]:
                    with st.expander(f"🖥️ {servidor}", expanded=True):
                        st.metric(label="CPU", value=f"{info['cpu']}%")
                        st.progress(min(info['cpu']/100, 1.0))
                        
                        st.metric(label="Memoria RAM", value=f"{info['ram']}%")
                        st.progress(min(info['ram']/100, 1.0))
                        
                        st.write(f"🌡️ Temperatura: N/A")
                        st.caption(f"Última actualización: {time.strftime('%H:%M:%S')}")
        else:
            st.info("Esperando conexión de agentes remotos...")

    time.sleep(2)