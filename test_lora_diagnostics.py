"""
Script de diagnóstico para depurar comunicación LoRa
Muestra información detallada de los dispositivos conectados
"""

import serial
import serial.tools.list_ports
import time
import sys

def find_lora_ports():
    """Encuentra puertos seriales disponibles"""
    ports = serial.tools.list_ports.comports()
    lora_ports = []
    
    for port in ports:
        if 'USB' in port.description or 'COM' in port.device or 'tty' in port.device:
            lora_ports.append(port)
    
    return lora_ports

def diagnose_device(port_name, device_name):
    """Diagnostica un dispositivo LoRa"""
    print(f"\n{'='*60}")
    print(f"Diagnosticando {device_name} en {port_name}")
    print('='*60)
    
    try:
        ser = serial.Serial(port_name, 115200, timeout=2)
        time.sleep(2)
        
        # Limpiar buffer
        ser.reset_input_buffer()
        
        # Esperar mensajes de inicio
        print("\n📋 Mensajes de inicio:")
        start_time = time.time()
        lines = []
        while time.time() - start_time < 3:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  {line}")
                    lines.append(line)
        
        # Solicitar STATUS
        print("\n🔍 Solicitando STATUS...")
        ser.write(b"STATUS\n")
        time.sleep(0.5)
        
        device_id = None
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"  {line}")
                if "STATUS:OK:ID:" in line:
                    device_id = line.split(":")[-1]
        
        # Solicitar RSSI
        print("\n📊 Solicitando RSSI...")
        ser.write(b"RSSI\n")
        time.sleep(0.5)
        
        rssi = None
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"  {line}")
                if "RSSI:" in line:
                    rssi = line.split(":")[-1]
        
        # Enviar PING
        print("\n🏓 Enviando PING...")
        ser.write(b"PING\n")
        time.sleep(0.5)
        
        pong_received = False
        while ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"  {line}")
                if "PONG" in line:
                    pong_received = True
        
        # Resumen
        print(f"\n{'='*60}")
        print(f"RESUMEN {device_name}:")
        print('='*60)
        print(f"✅ Puerto: {port_name}")
        print(f"{'✅' if device_id else '❌'} Device ID: {device_id if device_id else 'NO DETECTADO'}")
        print(f"{'✅' if rssi else '❌'} RSSI: {rssi if rssi else 'NO DISPONIBLE'}")
        print(f"{'✅' if pong_received else '❌'} Responde PING: {'SÍ' if pong_received else 'NO'}")
        
        # Verificar versión del firmware
        version_found = False
        magic_found = False
        for line in lines:
            if "v2.0" in line:
                version_found = True
                print(f"✅ Firmware: v2.0 (CON MAGIC BYTES)")
            elif "v1.0" in line:
                print(f"⚠️  Firmware: v1.0 (SIN MAGIC BYTES) - ACTUALIZAR!")
            if "PROTOCOL_MAGIC" in line:
                magic_found = True
                print(f"✅ Magic Bytes configurado: {line.split(':')[-1].strip()}")
        
        if not version_found:
            print(f"⚠️  No se detectó versión de firmware en mensajes de inicio")
        
        ser.close()
        return True
        
    except serial.SerialException as e:
        print(f"❌ Error al conectar: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  DIAGNÓSTICO DE COMUNICACIÓN LoRa P2P")
    print("="*60)
    
    # Encontrar puertos
    print("\n🔍 Buscando dispositivos...")
    ports = find_lora_ports()
    
    if not ports:
        print("❌ No se encontraron puertos seriales")
        return
    
    print(f"\n📋 Puertos encontrados: {len(ports)}")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")
    
    # Diagnosticar cada puerto
    if len(ports) == 1:
        print("\n⚠️  Solo se encontró 1 dispositivo")
        print("Para probar comunicación necesitas 2 dispositivos conectados\n")
        diagnose_device(ports[0].device, "Dispositivo 1")
    else:
        print(f"\n✅ Se encontraron {len(ports)} dispositivos")
        print("\nSelecciona los dispositivos a diagnosticar:")
        
        try:
            pc_idx = int(input(f"\nDispositivo PC (1-{len(ports)}): ")) - 1
            gw_idx = int(input(f"Dispositivo GW (1-{len(ports)}): ")) - 1
            
            if 0 <= pc_idx < len(ports) and 0 <= gw_idx < len(ports):
                diagnose_device(ports[pc_idx].device, "PC")
                diagnose_device(ports[gw_idx].device, "GW")
                
                print("\n" + "="*60)
                print("VERIFICACIONES FINALES")
                print("="*60)
                print("\n✅ Ambos dispositivos deben tener:")
                print("  - Firmware v2.0")
                print("  - PROTOCOL_MAGIC: 0x50505050")
                print("  - Device ID diferente (generado automáticamente)")
                print("  - Responder a PING con PONG")
                print("\n⚠️  Si alguno tiene v1.0 o no muestra PROTOCOL_MAGIC:")
                print("  1. Ejecuta: pio run -t upload")
                print("  2. Espera a que termine la carga")
                print("  3. Presiona el botón RESET del ESP32")
                print("  4. Vuelve a ejecutar este diagnóstico")
                
            else:
                print("❌ Índices inválidos")
        except ValueError:
            print("❌ Entrada inválida")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
