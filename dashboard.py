import streamlit as st
import requests
import pandas as pd
import time

# Configuración de la página
st.set_page_config(
    page_title="NOC - Monitoreo de Servidores",
    page_icon="🖥️",
    layout="wide"
)

st.title("🖥️ Panel de Control de Servidores (Real-Time)")

# Función para obtener datos de la API de forma segura
def obtener_datos():
    try:
        # Importante: Aquí usamos 127.0.0.1 porque el dashboard vive en la misma laptop que la API
        response = requests.get("http://127.0.0.1:8000/estado", timeout=1)
        if response.status_code == 200:
            return response.json()
    except Exception:
        # Si la API está caída o saturada, devolvemos un diccionario vacío
        # Esto evita el cartel rojo de error en la interfaz
        return {}
    return {}

# Contenedor para que la página se actualice sola
placeholder = st.empty()

while True:
    datos_servidores = obtener_datos()

    with placeholder.container():
        if not datos_servidores:
            st.warning("⚠️ Esperando datos de la API o servidores remotos...")
        else:
            # Creamos columnas: 3 por fila
            columnas = st.columns(3)
            
            for i, (nombre, info) in enumerate(datos_servidores.items()):
                with columnas[i % 3]:
                    # Determinar color según el uso de CPU (Alerta visual)
                    cpu_uso = info['cpu']
                    color_status = "normal"
                    if cpu_uso > 85:
                        st.error(f"🚨 ¡CRÍTICO: {nombre}!")
                    elif cpu_uso > 60:
                        st.warning(f"⚠️ Carga Alta: {nombre}")

                    # Crear la tarjeta visual
                    with st.expander(f"🖥️ {nombre}", expanded=True):
                        st.metric(label="CPU", value=f"{info['cpu']}%")
                        st.progress(info['cpu'] / 100)
                        
                        st.metric(label="Memoria RAM", value=f"{info['ram']}%")
                        st.progress(info['ram'] / 100)
                        
                        # Manejo de temperatura (si es 0, mostramos N/A)
                        temp_val = info.get('temp', 0)
                        label_temp = f"{temp_val}°C" if temp_val > 0 else "N/A (Sin Sensor)"
                        st.write(f"🌡️ **Temperatura:** {label_temp}")
                        
                        st.caption(f"Última actualización: {time.strftime('%H:%M:%S')}")

            # Opcional: Mostrar una tabla resumen al final
            st.divider()
            st.subheader("Resumen General")
            df = pd.DataFrame(datos_servidores).T
            st.table(df)

    # Tiempo de espera para la siguiente actualización
    time.sleep(2)