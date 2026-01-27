@echo off
title PANEL DE CONTROL NOC - Monitor de Servidores
color 0b

REM Nos movemos a la carpeta donde está el archivo .bat
cd /d "%~dp0"

REM Configurar encoding para caracteres especiales
chcp 65001 >nul

echo.
echo ==========================================
echo    INICIANDO MONITOR DE SERVIDORES NOC
echo ==========================================
echo.

REM 1. Iniciar el Servidor API
echo 📡 Iniciando Servidor de Datos...
start "NOC-API" /min venv\Scripts\python.exe -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

REM 2. Esperar 4 segundos
timeout /t 4 /nobreak >nul

REM 3. Iniciar el Dashboard
echo 📊 Lanzando Dashboard Visual...
venv\Scripts\python.exe -m streamlit run src\dashboard.py

echo.
echo ⚠️ Sistema en ejecución. No cierres esta ventana.
pause