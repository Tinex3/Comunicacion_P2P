@echo off
REM Script para iniciar con Docker en Windows

echo ======================================
echo   LoRa Chat Web - Docker
echo   Tekroy Desarrollos
echo ======================================
echo.

cd /d "%~dp0python_gui"

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no esta instalado
    echo.
    echo Instala Docker Desktop desde:
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker detectado correctamente
echo.

echo Construyendo imagen Docker...
docker-compose build

if %errorlevel% neq 0 (
    echo ERROR: No se pudo construir la imagen
    pause
    exit /b 1
)

echo.
echo Iniciando contenedor...
echo.
echo Accede a la aplicacion en:
echo   http://localhost:8000
echo.
echo Presiona Ctrl+C para detener
echo.

docker-compose up

pause
