"""
Script de diagnóstico para monitorear comunicación serial
Muestra todos los mensajes que llegan del ESP32
"""

import serial
import time
import sys

def monitor_serial(port='COM3', baudrate=115200):
    """
    Monitorea el puerto serial y muestra todos los mensajes
    """
    print(f"Conectando a {port}...")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Esperar estabilización
        
        print(f"✅ Conectado a {port}")
        print("=" * 60)
        print("Monitoreando puerto serial (Ctrl+C para salir)")
        print("=" * 60)
        print()
        
        buffer = ""
        
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                buffer += data
                
                # Procesar líneas completas
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    if line:
                        timestamp = time.strftime("%H:%M:%S")
                        
                        # Colorear según tipo de mensaje
                        if line.startswith("ERROR:"):
                            print(f"[{timestamp}] ❌ {line}")
                        elif line.startswith("RX:"):
                            print(f"[{timestamp}] 📥 {line}")
                        elif line.startswith("SENT:"):
                            print(f"[{timestamp}] 📤 {line}")
                        elif line.startswith("STATUS:"):
                            print(f"[{timestamp}] ℹ️  {line}")
                        elif line.startswith("PONG:"):
                            print(f"[{timestamp}] 🏓 {line}")
                        else:
                            print(f"[{timestamp}] ▪️  {line}")
            
            time.sleep(0.01)
            
    except serial.SerialException as e:
        print(f"❌ Error al conectar con {port}: {e}")
        print("\nPuertos disponibles:")
        import serial.tools.list_ports
        for port in serial.tools.list_ports.comports():
            print(f"  - {port.device}: {port.description}")
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor detenido")
        ser.close()

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else 'COM3'
    monitor_serial(port)
