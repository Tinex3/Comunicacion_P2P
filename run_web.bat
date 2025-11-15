@echo off
REM Script para iniciar LoRa Chat Web en Windows

echo ======================================
echo   LoRa P2P Chat Web - Iniciador
echo   Tekroy Desarrollos
echo ======================================
echo.

cd /d "%~dp0python_gui"

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo Python detectado correctamente
echo.

REM Verificar si las dependencias web están instaladas
python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependencias web...
    echo.
    pip install -r requirements-web.txt
    if %errorlevel% neq 0 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
    echo.
)

echo ======================================
echo   Iniciando servidor web...
echo ======================================
echo.
echo Accede a la aplicacion en:
echo   http://localhost:8000
echo.
echo Documentacion API:
echo   http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener
echo ======================================
echo.

REM Iniciar servidor
python web_server.py

if %errorlevel% neq 0 (
    echo.
    echo El servidor se cerro con errores
    pause
)
