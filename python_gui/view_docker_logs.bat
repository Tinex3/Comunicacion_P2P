@echo off
REM Script para ver logs del contenedor LoRa P2P Chat en tiempo real

echo ============================================
echo   Ver Logs del Contenedor LoRa P2P Chat
echo ============================================
echo.
echo Presiona Ctrl+C para salir
echo.

docker logs -f --tail 100 lora-p2p-chat
