@echo off
REM Script para iniciar la aplicación LoRa Chat en Windows
REM Autor: Tekroy Desarrollos

echo ======================================
echo   LoRa P2P Chat - Iniciador
echo   Tekroy Desarrollos
echo ======================================
echo.

REM Cambiar al directorio de la GUI
cd /d "%~dp0python_gui"

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor instala Python 3.7 o superior desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python detectado correctamente
echo.

REM Verificar si las dependencias están instaladas
python -c "import serial" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias...
    echo.
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo.
    echo Dependencias instaladas correctamente
    echo.
)

REM Ejecutar la aplicación
echo Iniciando aplicación...
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo La aplicación se cerró con errores
    pause
)
