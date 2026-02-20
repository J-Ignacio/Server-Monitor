@echo off
title HERRAMIENTAS NOC MONITOR
color 0b
cd /d "%~dp0"

:: ===== Verificar permisos de administrador =====
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ==========================================
    echo   Se requieren permisos de administrador
    echo ==========================================
    echo Solicitando elevacion...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)
:: ===============================================

:menu
cls
echo ==========================================
echo      HERRAMIENTAS DE DESARROLLO
echo ==========================================
echo.
echo  [1] Compilar Agentes (.exe)
echo  [2] Instalar Servicio Local (Dev)
echo  [3] Desinstalar Servicio Local (Dev)
echo  [4] Salir
echo.
set /p op=Seleccione una opcion: 

if "%op%"=="1" goto compilar
if "%op%"=="2" goto instalar
if "%op%"=="3" goto desinstalar
if "%op%"=="4" exit
goto menu

:: =================================================
:compilar
cls
echo ==========================================
echo      COMPILANDO EJECUTABLES
echo ==========================================
call venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install pywin32 --upgrade

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec >nul 2>&1

echo.
echo [1/2] Compilando Agente Portable...
pyinstaller --noconfirm --onefile --console --clean ^
--name "AGENTE_PORTABLE" ^
--paths=src ^
--hidden-import=psutil ^
--hidden-import=requests ^
--hidden-import=wmi ^
--hidden-import=config ^
src\agente.py

echo.
echo [2/2] Compilando Agente Servicio...
pyinstaller --noconfirm --onefile --console --clean ^
--name "NOC_SERVICIO" ^
--paths=src ^
--hidden-import=win32timezone ^
--hidden-import=servicemanager ^
--hidden-import=win32serviceutil ^
--hidden-import=win32service ^
--hidden-import=win32event ^
--hidden-import=psutil ^
--hidden-import=requests ^
--hidden-import=wmi ^
--hidden-import=agente ^
--hidden-import=config ^
src\agente_servicio.py

echo.
echo [3/3] Generando script de instalacion para clientes...
(
echo @echo off
echo net session ^>nul 2^>^&1
echo if %%errorlevel%% neq 0 ^(
echo     powershell -Command "Start-Process '%%~f0' -Verb RunAs"
echo     exit
echo ^)
echo echo ==========================================
echo echo   INSTALANDO AGENTE NOC ^(Remoto^)
echo echo ==========================================
echo echo.
echo cd /d "%%~dp0"
echo echo 1. Instalando servicio...
echo "%%~dp0NOC_SERVICIO.exe" install
echo sc config NOCMonitorAgente start= auto
echo timeout /t 2 /nobreak ^>nul
echo echo 2. Iniciando servicio...
echo sc start NOCMonitorAgente
echo echo.
echo echo [OK] Instalado correctamente.
echo pause
) > dist\instalar_agente.bat

echo.
echo ==========================================
echo [OK] Compilacion finalizada.
echo Revisa la carpeta 'dist/'
echo ==========================================
pause
goto menu

:: =================================================
:instalar
cls
echo ==========================================
echo      INSTALANDO SERVICIO LOCAL (DESARROLLO)
echo ==========================================

call venv\Scripts\activate
python -m pip install pywin32 --upgrade

cd src

echo.
echo Instalando servicio...
python -m win32serviceutil install agente_servicio.AgenteService --startup=auto
if %errorlevel% neq 0 (
    echo Error al instalar el servicio.
    pause
    cd ..
    goto menu
)

echo.
echo Iniciando servicio...
python -m win32serviceutil start agente_servicio.AgenteService

cd ..

echo.
echo ==========================================
echo [OK] Servicio instalado y ejecutandose.
echo ==========================================
pause
goto menu

:: =================================================
:desinstalar
cls
echo ==========================================
echo      DESINSTALANDO SERVICIO LOCAL
echo ==========================================

call venv\Scripts\activate
cd src

echo Deteniendo servicio...
python -m win32serviceutil stop agente_servicio.AgenteService >nul 2>&1

echo Eliminando servicio...
python -m win32serviceutil remove agente_servicio.AgenteService

cd ..

echo.
echo ==========================================
echo [OK] Servicio eliminado.
echo ==========================================
pause
goto menu
