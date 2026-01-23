@echo off
title PANEL DE CONTROL NOC - Monitor de Servidores
color 0b

REM Nos movemos a la carpeta donde está el archivo .bat
cd /d "%~dp0"

echo.
echo ==========================================
echo   INICIANDO MONITOR DE SERVIDORES NOC
echo ==========================================
echo.

REM Activar ambiente virtual
call venv\Scripts\activate.bat

echo ✓ Ambiente virtual activado
echo.

REM 1. Iniciar el Servidor API
echo 📡 Iniciando Servidor de Datos...
start "NOC-API" /min python -m uvicorn src.servidor:app --host 0.0.0.0 --port 8000

REM 2. Esperar 3 segundos
timeout /t 3 /nobreak >nul

REM 3. Iniciar el Dashboard usando el modulo de python directamente
REM Esto evita el error del launcher de streamlit.exe
echo 📊 Lanzando Dashboard Visual...
python -m streamlit run src\dashboard.py

echo.
echo ⚠️  Sistema en ejecución. No cierres esta ventana.
pause