"""
Script de prueba para verificar la detección de puertos serie
Muestra todos los puertos TTY/COM disponibles con información descriptiva
"""

import sys
import os

# Agregar python_gui al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_gui'))

try:
    from serial_comm import LoRaSerialCommunicator
    
    print("=" * 70)
    print("DETECCIÓN DE PUERTOS SERIE")
    print("=" * 70)
    print()
    
    ports = LoRaSerialCommunicator.list_available_ports()
    
    if ports:
        print(f"✅ Se encontraron {len(ports)} puerto(s):\n")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port}")
    else:
        print("❌ No se encontraron puertos serie disponibles")
        print("\nVerifica que:")
        print("  - El dispositivo ESP32 esté conectado vía USB")
        print("  - Los drivers estén instalados correctamente")
        print("  - El puerto no esté siendo usado por otra aplicación")
    
    print()
    print("=" * 70)
    
except ImportError as e:
    print(f"❌ Error: No se pudo importar pySerial")
    print(f"\nInstala las dependencias con:")
    print(f"  pip install -r python_gui/requirements.txt")
    print(f"\nError detallado: {e}")

except Exception as e:
    print(f"❌ Error inesperado: {e}")
