@echo off
title HERRAMIENTAS NOC MONITOR
color 0b
cd /d "%~dp0"

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

:compilar
cls
echo ==========================================
echo      COMPILANDO EJECUTABLES
echo ==========================================
call venv\Scripts\activate
pip install pywin32 --upgrade
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec

echo.
echo [1/2] Compilando Agente Portable...
pyinstaller --noconfirm --onefile --console --clean --name "AGENTE_PORTABLE" --hidden-import=psutil --hidden-import=requests --hidden-import=wmi src\agente.py

echo.
echo [2/2] Compilando Agente Servicio...
pyinstaller --noconfirm --onefile --console --clean --name "NOC_SERVICIO" --hidden-import=win32timezone --hidden-import=servicemanager --hidden-import=win32serviceutil --hidden-import=win32service --hidden-import=win32event --hidden-import=psutil --hidden-import=requests --hidden-import=wmi src\agente_servicio.py

echo.
echo [3/3] Generando script de instalacion para clientes...
(
echo @echo off
echo echo ==========================================
echo echo   INSTALANDO AGENTE NOC ^(Remoto^)
echo echo ==========================================
echo echo.
echo echo IMPORTANTE: Ejecutar como Administrador
echo echo.
echo cd /d "%%~dp0"
echo.
echo echo 1. Instalando servicio...
echo NOC_SERVICIO.exe install --startup=auto
echo.
echo echo 2. Iniciando servicio...
echo NOC_SERVICIO.exe start
echo.
echo echo.
echo echo [OK] Instalado correctamente.
echo echo No olvides editar config/config.json con la IP del servidor.
echo pause
) > dist\instalar_agente.bat

echo.
echo [OK] Compilacion finalizada. Revisa la carpeta 'dist/'
pause
goto menu

:instalar
cls
echo ==========================================
echo      INSTALANDO SERVICIO LOCAL
echo ==========================================
call venv\Scripts\activate
pip install pywin32
python src\agente_servicio.py install --startup=auto
python src\agente_servicio.py start
echo.
echo [OK] Servicio instalado.
pause
goto menu

:desinstalar
cls
echo ==========================================
echo      DESINSTALANDO SERVICIO LOCAL
echo ==========================================
call venv\Scripts\activate
python src\agente_servicio.py remove
echo.
echo [OK] Servicio eliminado.
pause
goto menu