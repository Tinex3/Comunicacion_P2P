#!/bin/bash
# Script para iniciar la aplicación LoRa Chat en Linux/Mac
# Autor: Tekroy Desarrollos

echo "======================================"
echo "  LoRa P2P Chat - Iniciador"
echo "  Tekroy Desarrollos"
echo "======================================"
echo

# Cambiar al directorio del script
cd "$(dirname "$0")/python_gui"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo
    echo "Por favor instala Python 3.7 o superior"
    exit 1
fi

echo "Python detectado correctamente"
echo

# Verificar si las dependencias están instaladas
if ! python3 -c "import serial" &> /dev/null; then
    echo "Instalando dependencias..."
    echo
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
    echo
    echo "Dependencias instaladas correctamente"
    echo
fi

# Ejecutar la aplicación
echo "Iniciando aplicación..."
echo
python3 main.py

if [ $? -ne 0 ]; then
    echo
    echo "La aplicación se cerró con errores"
    read -p "Presiona Enter para continuar..."
fi
