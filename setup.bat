@echo off
title PANEL DE CONTROL NOC - Monitor de Servidores
color 0b

REM Configura la terminal para mostrar iconos correctamente
chcp 65001 >nul

REM Se asegura de estar en la carpeta donde reside el archivo .bat
cd /d "%~dp0"

echo.
echo ==========================================
echo    INICIANDO MONITOR DE SERVIDORES NOC
echo ==========================================
echo.

REM Ejecución directa usando la ruta del entorno virtual (venv)
REM Esto evita errores de "python no reconocido" o problemas de PATH

echo 📡 Iniciando Servidor de Datos (API)...
start "NOC-API" /min venv\Scripts\python.exe -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

echo ⏳ Esperando respuesta del servidor...
timeout /t 4 /nobreak >nul

echo 📊 Lanzando Dashboard Visual con Streamlit...
venv\Scripts\python.exe -m streamlit run src\dashboard.py

echo.
echo ------------------------------------------
echo ⚠️  Sistema en ejecución. No cierres esta ventana.
echo ------------------------------------------
pause