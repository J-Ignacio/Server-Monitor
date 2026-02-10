# 🛠️ Guía de Instalación Paso a Paso

## Central (Laptop NOC)

### Opción A: Ejecutable (Más Fácil)

1. **Descargar/extraer el proyecto**
2. **Doble clic en `Iniciar_NOC.bat`**
   - Se abre ventana con API
   - Se abre Dashboard automáticamente
3. **Acceder a Dashboard:** `http://localhost:8501`

### Opción B: Manual (Desarrollo)

```powershell
# 1. Preparar entorno
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Terminal 1: Iniciar API
python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

# 3. Terminal 2: Iniciar Dashboard
streamlit run src/dashboard.py
```

### Configuración Firewall (Primera vez)

**Windows (PowerShell como Admin):**
```powershell
netsh advfirewall firewall add rule name="NOC Monitor" dir=in action=allow protocol=tcp localport=8000
```

---

## Servidor Remoto

### Opción A: Con Ejecutable (Recomendado)

1. **Acceder por RDP al servidor**
   ```cmd
   mstsc /v:192.168.1.100
   ```

2. **Copiar `AGENTE_FINAL.exe`** a una carpeta (ej: `C:\Monitor\`)

3. **Ejecutar `AGENTE_FINAL.exe`**
   - Se creará automáticamente la carpeta `config/`.
   - Si no conecta, cierra el programa.
   - Edita `config/config.json` y pon la IP correcta.
   - Vuelve a abrir `AGENTE_FINAL.exe`.

### Opción B: Con Script Python

1. **Copiar `src/agente.py`** al servidor

2. **Instalar dependencias:**
   ```powershell
   pip install requests psutil wmi
   ```

3. **Editar `agente.py`** línea 8:
   ```python
   IP_CENTRAL = "192.168.4.143"  # Cambiar con tu IP
   ```

4. **Ejecutar:**
   ```powershell
   python agente.py
   ```

---

## Verificación

✅ Dashboard muestra servidores: `http://localhost:8501`  
✅ API responde: `http://localhost:8000/estado`  
✅ Agente reporta "✓ Datos enviados"

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Dashboard no abre | Verificar `http://localhost:8501` en navegador |
| "Port 8000 in use" | Cambiar puerto o cerrar proceso que lo usa |
| "Sin conexión" en agente | Verificar IP_CENTRAL es correcta |
| Permisos denegados en .bat | Ejecutar como Administrador |
