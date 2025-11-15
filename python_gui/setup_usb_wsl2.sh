#!/bin/bash
# setup_usb_wsl2.sh
# Script para configurar puertos USB en WSL2 (Windows)
#
# Requisitos:
#   1. WSL2 instalado
#   2. usbipd-win instalado en Windows: winget install usbipd
#   3. Herramientas USBIP en WSL2
#
# Uso:
#   ./setup_usb_wsl2.sh

echo "=========================================="
echo "Configuración USB para WSL2"
echo "=========================================="
echo

# Verificar si estamos en WSL2
if ! grep -qi microsoft /proc/version; then
    echo "❌ Este script debe ejecutarse en WSL2"
    exit 1
fi

echo "✅ WSL2 detectado"
echo

# Instalar herramientas USBIP si no están instaladas
if ! command -v usbip &> /dev/null; then
    echo "📦 Instalando herramientas USBIP..."
    sudo apt update
    sudo apt install -y linux-tools-virtual hwdata
    sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*/usbip 20
else
    echo "✅ USBIP ya está instalado"
fi

echo
echo "=========================================="
echo "Instrucciones para conectar dispositivo USB:"
echo "=========================================="
echo
echo "1. En PowerShell (como Administrador) en Windows, ejecuta:"
echo "   usbipd list"
echo
echo "2. Identifica el BUSID de tu dispositivo ESP32 (ej: 1-4)"
echo
echo "3. Conecta el dispositivo a WSL2:"
echo "   usbipd bind --busid <BUSID>"
echo "   usbipd attach --wsl --busid <BUSID>"
echo
echo "4. Verifica en WSL2 que el dispositivo esté disponible:"
echo "   ls -la /dev/ttyUSB* /dev/ttyACM*"
echo
echo "5. Ejecuta Docker Compose:"
echo "   docker-compose up"
echo
echo "=========================================="
echo

# Verificar dispositivos actuales
echo "Dispositivos serie actuales en WSL2:"
ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "  Ninguno detectado"
echo

echo "✅ Configuración completa"
