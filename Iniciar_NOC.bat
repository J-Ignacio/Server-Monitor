@echo off
title PANEL DE CONTROL NOC
color 0b

:: Nos movemos a la carpeta donde esta el archivo .bat
cd /d "%~dp0"

echo ==========================================
echo    INICIANDO MONITOR DE SERVIDORES NOC
echo ==========================================
echo.

:: 1. Iniciar el Servidor API
echo [+] Iniciando Servidor de Datos...
start "NOC-API" /min .\venv\Scripts\python.exe src\servidor.py

:: 2. Esperar 3 segundos
timeout /t 3 /nobreak >nul

:: 3. Iniciar el Dashboard usando el modulo de python directamente
:: Esto evita el error del launcher de streamlit.exe
echo [+] Lanzando Dashboard Visual...
.\venv\Scripts\python.exe -m streamlit run src\dashboard.py

echo.
echo [!] Sistema en ejecucion. No cierres esta ventana.
pause