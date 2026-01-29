@echo off
title LIMPIEZA DE PROYECTO
color 0e

echo.
echo ==========================================
echo    LIMPIEZA DE ARCHIVOS TEMPORALES
echo ==========================================
echo.
echo ESTO BORRARA:
echo  - Entorno virtual (venv)
echo  - Carpetas de compilacion (build, dist)
echo  - Archivos temporales de Python
echo  - Configuracion local (config.json)
echo.
set /p confirm="Estas seguro? (S/N): "
if /i "%confirm%" neq "S" exit /b

echo.
echo [1/4] Borrando entorno virtual...
if exist venv rmdir /s /q venv

echo [2/4] Borrando compilaciones...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo [3/4] Borrando cache de Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo [4/4] Borrando configuracion local...
if exist config\config.json del config\config.json

echo.
echo [LISTO] Proyecto limpio.
echo Ejecuta setup.bat para reinstalar.
pause
