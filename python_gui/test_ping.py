"""
Script de prueba para verificar la funcionalidad PING/PONG
Detecta automáticamente puertos con dispositivos LoRa P2P
"""

from serial_comm import LoRaSerialCommunicator
import sys

def main():
    print("=" * 60)
    print("Test de Auto-detección de Dispositivos LoRa P2P")
    print("=" * 60)
    print()
    
    # 1. Listar todos los puertos disponibles
    print("📋 Listando todos los puertos serie disponibles...")
    all_ports = LoRaSerialCommunicator.list_available_ports()
    
    if not all_ports:
        print("❌ No se encontraron puertos serie en el sistema")
        return
    
    print(f"✅ {len(all_ports)} puerto(s) encontrado(s):")
    for i, port in enumerate(all_ports, 1):
        print(f"   {i}. {port}")
    print()
    
    # 2. Detectar puertos con dispositivos LoRa
    print("🔍 Detectando dispositivos LoRa P2P (esto puede tardar unos segundos)...")
    print()
    
    def progress_callback(port, current, total):
        port_name = port.split(' - ')[0]
        print(f"   [{current}/{total}] Probando {port_name}...", end='\r')
    
    lora_ports = LoRaSerialCommunicator.detect_lora_ports(progress_callback)
    print(" " * 80, end='\r')  # Limpiar línea
    
    # 3. Mostrar resultados
    print()
    print("=" * 60)
    print("RESULTADOS DE LA DETECCIÓN")
    print("=" * 60)
    
    if lora_ports:
        print(f"✅ {len(lora_ports)} dispositivo(s) LoRa P2P encontrado(s):")
        print()
        for i, port in enumerate(lora_ports, 1):
            print(f"   {i}. {port}")
        print()
        print("✨ Puedes conectarte a cualquiera de estos puertos directamente")
    else:
        print("❌ No se detectaron dispositivos LoRa P2P")
        print()
        print("Posibles causas:")
        print("   • El dispositivo no está conectado")
        print("   • El firmware no tiene el comando PING implementado")
        print("   • El puerto está siendo usado por otra aplicación")
        print("   • El dispositivo no ha terminado de inicializarse")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
