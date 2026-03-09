# Guía de Instalación

## Servidor Central (Nodo NOC)

### Opción A: Ejecución Automatizada (Recomendado)

1. **Extraiga el archivo del proyecto** en un directorio dedicado.
2. **Ejecute `Iniciar_NOC.bat`**
   - Inicializa el servicio FastAPI en el puerto 8000.
   - Lanza automáticamente el Dashboard de Streamlit.
3. **Acceda al Dashboard:** Navegue a `http://localhost:8501` en su navegador web.

### Opción B: Ejecución Manual (Entorno de Desarrollo)

```powershell
# 1. Prepare el entorno de Python
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Terminal 1: Inicialice la API
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# 3. Terminal 2: Inicialice el Dashboard
streamlit run src/dashboard.py
```

### Configuración del Firewall (Configuración Inicial)

**Windows (PowerShell como Administrador):**
```powershell
netsh advfirewall firewall add rule name="Monitor NOC" dir=in action=allow protocol=tcp localport=8000
```

---

## Agente Remoto

### Opción A: Ejecutable Compilado (Recomendado)

1. **Acceda al servidor remoto** vía RDP:
   ```cmd
   mstsc /v:<IP_SERVIDOR>
   ```

2. **Implemente el Ejecutable:** Copie `AGENTE_PORTABLE.exe` a un directorio designado (ej. `C:\Monitor\`).

3. **Inicialice el Agente:** Ejecute `AGENTE_PORTABLE.exe`.
   - La aplicación generará automáticamente el directorio `config/`.
   - Si la conexión falla inicialmente, termine el proceso.
   - Modifique `config/config.json` para especificar la IP correcta del Servidor Central.
   - Reinicie `AGENTE_PORTABLE.exe`.

### Opción B: Ejecución desde el Código Fuente de Python

1. **Implemente el Código Fuente:** Copie `src/agente.py` al servidor remoto.

2. **Instale las Dependencias:**
   ```powershell
   pip install requests psutil wmi
   ```

3. **Configure la IP Central:** Edite `agente.py` (Línea 8) o configure vía `config/config.json`:
   ```python
   IP_CENTRAL = "192.168.4.143"  # Reemplace con la IP del Servidor Central
   ```

4. **Ejecute:**
   ```powershell
   python agente.py
   ```

---

## Verificación del Sistema

- **Dashboard:** Confirme que los nodos se cargan en `http://localhost:8501`
- **Estado de la API:** Verifique la respuesta JSON en `http://localhost:8000/estado`
- **Registros del Agente:** Confirme que la salida de la consola indique "Datos transmitidos"

---

## Solución de Problemas

| Problema | Resolución |
|-------|------------|
| El Dashboard no abre | Verifique que `http://localhost:8501` sea accesible en el navegador. |
| Error "Puerto 8000 en uso" | Reasigne el puerto en la configuración o termine el proceso conflictivo. |
| El agente reporta "Error de conexión" | Verifique que `IP_CENTRAL` sea correcta y que el firewall permita tráfico en el puerto 8000. |
| Acceso denegado al ejecutar `.bat` | Ejecute el script batch con privilegios de Administrador. |

## Habilitando Métricas de Temperatura (Windows)

Si el dashboard muestra "Temperatura: N/A", la interfaz WMI de Windows no está transmitiendo datos de los sensores de forma nativa.

**Resolución:**
1. Descargue y extraiga [OpenHardwareMonitor](https://openhardwaremonitor.org/).
2. Ejecute `OpenHardwareMonitor.exe` como **Administrador**.
3. Navegue a **Options** (Opciones) y habilite:
   - "Run on Windows Startup" (Ejecutar al iniciar Windows)
   - "Minimize to Tray" (Minimizar a la bandeja del sistema)
4. Mantenga la aplicación minimizada; el agente consultará automáticamente las métricas expuestas de WMI.
