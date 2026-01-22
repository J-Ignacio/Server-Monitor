@echo off
REM Script de configuración automática para otra PC

title Setup - Monitor de Servidores NOC
color 0a

cd /d "%~dp0"

echo.
echo =========================================
echo   SETUP - Monitor de Servidores NOC
echo =========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en PATH
    echo Descarga desde: https://www.python.org/downloads/
    echo Recuerda marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)

echo [1] Creando ambiente virtual...
if not exist venv (
    python -m venv venv
    echo [OK] Ambiente virtual creado
) else (
    echo [OK] Ambiente virtual ya existe
)

echo.
echo [2] Activando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo [3] Actualizando pip...
python -m pip install --upgrade pip >nul 2>&1

echo.
echo [4] Instalando dependencias...
pip install -r requeriments.txt
if errorlevel 1 (
    echo [ERROR] Fallo al instalar dependencias
    pause
    exit /b 1
)

echo.
echo [5] Regenerando AGENTE_FINAL.exe...
pip install pyinstaller >nul 2>&1
pyinstaller AGENTE_FINAL.spec >nul 2>&1
if exist dist\AGENTE_FINAL.exe (
    echo [OK] AGENTE_FINAL.exe generado correctamente
) else (
    echo [ADVERTENCIA] No se pudo generar AGENTE_FINAL.exe
    echo Intenta ejecutar manualmente: pyinstaller AGENTE_FINAL.spec
)

echo.
echo =========================================
echo   ✅ CONFIGURACIÓN COMPLETADA
echo =========================================
echo.
echo Próximos pasos:
echo 1. Doble clic en: Iniciar_NOC.bat
echo 2. El dashboard se abrirá automáticamente
echo 3. Acceder a: http://localhost:8501
echo.
pause
