@echo off
title PANALCOR — Servidor Local
color 0A
cls
echo.
echo  ==========================================
echo   PANALCOR S.L. — Servidor de Mantenimiento
echo  ==========================================
echo.
echo  Comprobando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python no esta instalado.
    echo.
    echo  Descargalo GRATIS en: https://www.python.org/downloads/
    echo  - Descarga "Python 3.x.x"
    echo  - Durante la instalacion marca: "Add python.exe to PATH"
    echo  - Vuelve a hacer doble clic en este archivo
    echo.
    pause
    exit
)
echo  Python encontrado. Arrancando servidor...
echo.
cd /d "%~dp0"
python servidor.py
echo.
echo  Servidor detenido.
pause
