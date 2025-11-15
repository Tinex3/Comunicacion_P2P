#!/bin/bash
# Script para iniciar LoRa Chat Web en Linux/Mac

echo "======================================"
echo "  LoRa P2P Chat Web - Iniciador"
echo "  Tekroy Desarrollos"
echo "======================================"
echo

cd "$(dirname "$0")/python_gui"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    exit 1
fi

echo "Python detectado correctamente"
echo

# Verificar si las dependencias están instaladas
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Instalando dependencias web..."
    echo
    pip3 install -r requirements-web.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudieron instalar las dependencias"
        exit 1
    fi
    echo
fi

echo "======================================"
echo "  Iniciando servidor web..."
echo "======================================"
echo
echo "Accede a la aplicación en:"
echo "  http://localhost:8000"
echo
echo "Documentación API:"
echo "  http://localhost:8000/docs"
echo
echo "Presiona Ctrl+C para detener"
echo "======================================"
echo

# Iniciar servidor
python3 web_server.py

if [ $? -ne 0 ]; then
    echo
    echo "El servidor se cerró con errores"
    read -p "Presiona Enter para continuar..."
fi
