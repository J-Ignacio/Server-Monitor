@echo off
REM Script universal para Windows - Setup inicial

setlocal enabledelayedexpansion

title Setup - Monitor de Servidores NOC
color 0a

cd /d "%~dp0"

echo.
echo ========================================
echo   SISTEMA DE MONITOREO NOC - SETUP
echo ========================================
echo.

REM Detectar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH
    echo.
    echo Descargue Python desde: https://www.python.org/downloads/
    echo Asegúrese de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo ✓ Python detectado
python --version

REM Crear ambiente virtual
echo.
echo 📦 Creando ambiente virtual...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error al crear el ambiente virtual
        pause
        exit /b 1
    )
    echo ✓ Ambiente virtual creado
) else (
    echo ✓ Ambiente virtual ya existe
)

REM Activar ambiente virtual
echo.
echo 🔧 Activando ambiente virtual...
call venv\Scripts\activate.bat

REM Actualizar pip
echo.
echo 📥 Actualizando pip...
python -m pip install --upgrade pip >nul 2>&1

REM Instalar dependencias
echo.
echo 📚 Instalando dependencias...
pip install -r requeriments.txt
if errorlevel 1 (
    echo ❌ Error al instalar dependencias
    pause
    exit /b 1
)

REM Crear directorio de configuración
echo.
echo 📁 Creando directorios...
if not exist "config" mkdir config
if not exist "logs" mkdir logs

REM Crear archivo de configuración
echo.
echo ⚙️  Configuración inicial...
if not exist "config\config.json" (
    python -c "from src.config import guardar_config, CONFIGURACION_PREDETERMINADA; guardar_config(CONFIGURACION_PREDETERMINADA)"
    echo ✓ Archivo de configuración creado en: config/config.json
    echo.
    echo ⚠️  IMPORTANTE: Editar config/config.json con la IP de su NOC
) else (
    echo ✓ Configuración ya existe
)

echo.
echo [5] Regenerando AGENTE_FINAL.exe...
pip install pyinstaller >nul 2>&1
pyinstaller AGENTE_FINAL.spec >nul 2>&1
if exist dist\AGENTE_FINAL.exe (
    echo ✓ AGENTE_FINAL.exe generado correctamente
) else (
    echo ⚠️  No se pudo generar AGENTE_FINAL.exe
    echo Intenta ejecutar manualmente: pyinstaller AGENTE_FINAL.spec
)

echo.
echo ✅ Setup completado correctamente
echo.
echo Próximos pasos:
echo 1. Editar config/config.json con la IP correcta de su NOC
echo 2. En NOC: Ejecute Iniciar_NOC.bat
echo 3. En servidores: Ejecute agente.py o AGENTE_FINAL.exe
echo.
pause
