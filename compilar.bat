@echo off
echo ==================================================
echo   GENERADOR DE EJECUTABLES (NOC MONITOR)
echo ==================================================
echo.

call venv\Scripts\activate

echo 1. Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec

echo.
echo 2. Compilando Agente Portable (Manual)...
pyinstaller --noconfirm --onefile --console --name "AGENTE_PORTABLE" --hidden-import=psutil --hidden-import=requests --hidden-import=wmi src\agente.py

echo.
echo 3. Compilando Agente Servicio (Windows Service)...
pyinstaller --noconfirm --onefile --console --name "NOC_SERVICIO" --hidden-import=win32timezone --hidden-import=psutil --hidden-import=requests --hidden-import=wmi src\agente_servicio.py

echo.
@echo off
echo ==================================================
echo   GENERADOR DE EJECUTABLES (NOC MONITOR)
echo ==================================================
echo.

call venv\Scripts\activate

echo 1. Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
del /q *.spec

echo.
echo 2. Compilando Agente Portable (Manual)...
pyinstaller --noconfirm --onefile --console --name "AGENTE_PORTABLE" --hidden-import=psutil --hidden-import=requests --hidden-import=wmi src\agente.py

echo.
echo 3. Compilando Agente Servicio (Windows Service)...
pyinstaller --noconfirm --onefile --console --name "NOC_SERVICIO" --hidden-import=win32timezone --hidden-import=psutil --hidden-import=requests --hidden-import=wmi src\agente_servicio.py

echo.
echo [OK] Compilacion finalizada. Revisa la carpeta 'dist/'
pause
echo [OK] Compilacion finalizada. Revisa la carpeta 'dist/'
pause