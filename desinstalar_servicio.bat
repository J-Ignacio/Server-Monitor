@echo off
echo ==================================================
echo   DESINSTALADOR DE SERVICIO (NOC AGENTE)
echo ==================================================
echo.
echo IMPORTANTE: Ejecutar como ADMINISTRADOR.
echo.
pause

call venv\Scripts\activate

echo Deteniendo y eliminando servicio...
python src\agente_servicio.py remove

echo.
@echo off
echo ==================================================
echo   DESINSTALADOR DE SERVICIO (NOC AGENTE)
echo ==================================================
echo.
echo IMPORTANTE: Ejecutar como ADMINISTRADOR.
echo.
pause

call venv\Scripts\activate

echo Deteniendo y eliminando servicio...
python src\agente_servicio.py remove

echo.
echo [OK] Servicio eliminado correctamente.
pause
echo [OK] Servicio eliminado correctamente.
pause