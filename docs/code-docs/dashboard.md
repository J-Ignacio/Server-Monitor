# Technical Documentation: Visualization Dashboard `(dashboard.py)`
The Dashboard is an interactive web application that consumes the central server's API to display the status of all connected agents in real time.

## 🛠️ Detailed Analysis by Modules

### 1. Interface Configuration and Dynamic Styling

Streamlit allows injecting CSS to customize the appearance. This block manages the "Dark Mode" and the base structure of the page.

```python
import streamlit as st
import requests
import time
import pandas as pd
import os
import base64
from src.config import DASHBOARD_INTERVALO, SERVIDOR_CENTRAL_PUERTO

# Configure page
st.set_page_config(page_title="NOC Monitor", layout="wide")

# --- Theme Configuration (Sidebar) ---
with st.sidebar:
    # Company logo
    logo_path = BASE_DIR / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), use_column_width=True)
    
    # --- CSV Export Button ---
    if st.button("📥 Download CSV Report"):
        try:
            df_export = pd.DataFrame(obtener_datos().values())
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Save CSV", csv, "reporte_noc.csv", "text/csv")
        except Exception as e:
            st.error(f"Error: {e}")
            
    st.subheader("⚙️ Preferences")
    frecuencia_refresh = st.slider("Refresh Rate (s)", min_value=1, max_value=30, value=2)
    modo_compacto = st.toggle("Compact View", value=False)

# --- Glassmorphism / Dark NOC CSS Styling ---
custom_css = """
<style>
    /* Custom styles for glass effect and professional dark mode */
    .stApp { background-color: #050505; ... }
    .server-card { background: rgba(255, 255, 255, 0.03); ... }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)
st.markdown('<div class="noc-title">🖥️ NOC MONITOR</div>', unsafe_allow_html=True)
```

- `st.set_page_config(layout="wide")`: Uses the full width of the screen, ideal for viewing multiple servers in columns.

- **CSV Export:** `st.download_button` is used to allow the user to download a snapshot of the current data. Pandas converts the data dictionary to CSV format in memory before downloading.

- **CSS Injection:** `unsafe_allow_html=True` is used to force styles that Streamlit does not allow modifying by default, such as the background color of expandable containers.

### 2. API Data Consumption

The dashboard does not read the database directly; it queries the central server endpoints.

```python
# Container that updates dynamically
placeholder = st.empty()

def obtener_datos():
    """Gets metrics from the central server"""
    try:
        # It points to 127.0.0.1 because the Dashboard usually runs on the same host as the API
        response = requests.get(f"http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/estado", timeout=2)
        protocolo = "https" if USAR_SSL else "http"
        response = requests.get(f"{protocolo}://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/estado", timeout=2, verify=VERIFICAR_SSL)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        st.warning(f"⚠️ Cannot connect to local API")
        return {}
```

- `st.empty()`: Creates a placeholder in the interface. This allows the dashboard to be "cleared" and redrawn in each cycle without accumulating elements downward.

- **SSL Support:** The code dynamically selects between `http://` and `https://` based on the `USAR_SSL` variable. If SSL is used, certificate verification is also handled with `verify=VERIFICAR_SSL`.

- **Encapsulation:** By using the central API, the dashboard remains lightweight and decoupled from the database logic.

### 3. Server Rendering and Historical Charts

This block processes the server list and generates dynamic columns with metrics and performance charts.

```python
# Constant update loop
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

                    # --- State Calculation (Online/Offline) ---
                    timestamp_str = info.get('timestamp', '')
                    estado_icono = "❓"
                    if timestamp_str:
                        last_seen = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        diff = (datetime.utcnow() - last_seen).total_seconds()
                        # Green < 30s, Yellow < 60s, Red > 60s
                        estado_icono = "🟢" if diff < 30 else ("🟡" if diff < 60 else "🔴")

                    with cols[i]:
                        with st.expander(f"🖥️ {servidor}", expanded=True):
                        with st.expander(f"{estado_icono} {servidor}", expanded=True):
                            st.metric(label="CPU", value=f"{info['cpu']}%")
                            st.progress(min(info['cpu']/100, 1.0))
                            
                            # ... (RAM, Disk, and Temperature Metrics) ...

                            # --- Historical Chart ---
                            try:
                                url_hist = f"http://127.0.0.1:{SERVIDOR_CENTRAL_PUERTO}/historial/{servidor}"
                                resp = requests.get(url_hist, timeout=1)
                                if resp.status_code == 200:
                                    df = pd.DataFrame(resp.json())
                                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                                    st.line_chart(df.set_index("timestamp")["cpu"], height=150)
                            except: pass
                            
                            # --- Reboot Button with Confirmation ---
                            if not st.session_state[f"conf_{servidor}"]:
                                st.button("🔄 Reboot", key=f"btn_{servidor}", ...)
                            else:
                                st.warning("Are you sure?")
                                col_si, col_no = st.columns(2)
                                with col_si:
                                    st.button("✅ Yes", on_click=enviar_orden, args=(servidor,))
```

- `st.columns`: Creates a dynamic grid. If 3 agents are connected, 3 columns are created automatically.

- **Status Indicator:** Calculates the time difference between the `timestamp` of the last report and the current time (`utcnow`). If more than 60 seconds have passed, the icon changes to red 🔴, indicating possible disconnection.

- **State Management (Session State):** For the reboot button, `st.session_state` is used to remember if the user has pressed "Reboot" and display the confirmation buttons ("Yes/No") without reloading the whole page.

- `st.line_chart`: Uses Pandas to process the history and display a line chart of CPU usage. It is crucial to convert the `timestamp` to a `datetime` object so that the X-axis is chronological.

### 4. Alert System (Visual and Audio)

One of the most important functions for a NOC (Network Operations Center) is immediate notification of failures.

```python
                # --- Alert Trigger (Audio + Visual) ---
                if alerta_critica:
                    st.error("🔥 CRITICAL ALERT! CPU usage above 90% detected.")
                    sound_file = "alert.mp3"
                    if os.path.exists(sound_file):
                        try:
                            with open(sound_file, "rb") as f:
                                data = f.read()
                                b64 = base64.b64encode(data).decode()
                                # HTML5 injection for audio auto-play
                                st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                        except: pass
```                        

- **Base64 Audio:** Since Streamlit does not have a native "sound alarm" component, a local MP3 file is read, encoded in Base64, and an HTML5 `<audio autoplay>` tag is injected.

- **Threshold Logic:** The `alerta_critica` variable is activated if any server in the loop exceeds 90% CPU.

### 5. Loop Control
```python
    except Exception as e:
        st.error(f"Error: {e}")
    
    time.sleep(DASHBOARD_INTERVALO)
```

- `time.sleep`: Controls the refresh rate. A typical value is 2-5 seconds to avoid overloading the browser and the API.