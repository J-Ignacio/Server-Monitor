@echo off
echo ==================================================
echo   INSTALADOR DE SERVICIO WINDOWS (NOC AGENTE)
echo ==================================================
echo.
echo IMPORTANTE: Este script debe ejecutarse como ADMINISTRADOR.
echo.
pause

call venv\Scripts\activate
pip install pywin32

echo Instalando servicio...
python src\agente_servicio.py install --startup=auto
python src\agente_servicio.py start

echo.
@echo off
echo ==================================================
echo   INSTALADOR DE SERVICIO WINDOWS (NOC AGENTE)
echo ==================================================
echo.
echo IMPORTANTE: Este script debe ejecutarse como ADMINISTRADOR.
echo.
pause

call venv\Scripts\activate
pip install pywin32

echo Instalando servicio...
python src\agente_servicio.py install --startup=auto
python src\agente_servicio.py start

echo.
echo [OK] Servicio instalado. Verifica en services.msc buscando "NOC Monitor Agente"
pause
echo [OK] Servicio instalado. Verifica en services.msc buscando "NOC Monitor Agente"
pause