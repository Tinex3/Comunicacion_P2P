"""
Módulo de comunicación serial con ESP32 LoRa
Gestiona el envío y recepción de mensajes a través del puerto serial
"""

import serial
import serial.tools.list_ports
import threading
import time
from typing import Callable, Optional, List


class LoRaSerialCommunicator:
    """Clase para manejar la comunicación serial con el módulo LoRa"""
    
    def __init__(self, baudrate: int = 115200):
        """
        Inicializa el comunicador serial
        
        Args:
            baudrate: Velocidad de comunicación (default: 115200)
        """
        self.baudrate = baudrate
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.read_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Callbacks
        self.on_message_received: Optional[Callable] = None
        self.on_status_update: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
    @staticmethod
    def list_available_ports() -> List[str]:
        """
        Lista todos los puertos COM disponibles
        
        Returns:
            Lista de nombres de puertos disponibles
        """
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str) -> bool:
        """
        Conecta al puerto serial especificado
        
        Args:
            port: Nombre del puerto (ej: 'COM3' o '/dev/ttyUSB0')
            
        Returns:
            True si la conexión fue exitosa
        """
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            
            # Esperar a que el ESP32 se inicialice
            time.sleep(2)
            
            # Limpiar buffer
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()
            
            self.is_connected = True
            
            # Iniciar thread de lectura
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            # Solicitar estado
            self.request_status()
            
            return True
            
        except serial.SerialException as e:
            if self.on_error:
                self.on_error(f"Error de conexión: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconecta del puerto serial"""
        self.running = False
        
        if self.read_thread:
            self.read_thread.join(timeout=2)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.is_connected = False
    
    def send_message(self, sender_name: str, message: str) -> bool:
        """
        Envía un mensaje vía LoRa
        
        Args:
            sender_name: Nombre del remitente
            message: Contenido del mensaje
            
        Returns:
            True si el mensaje se envió correctamente
        """
        if not self.is_connected or not self.serial_port:
            if self.on_error:
                self.on_error("No hay conexión con el dispositivo")
            return False
        
        try:
            # Formato: TX:Nombre:Mensaje\n
            command = f"TX:{sender_name}:{message}\n"
            self.serial_port.write(command.encode('utf-8'))
            self.serial_port.flush()
            return True
            
        except serial.SerialException as e:
            if self.on_error:
                self.on_error(f"Error al enviar: {str(e)}")
            return False
    
    def request_status(self) -> bool:
        """Solicita el estado del dispositivo"""
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(b"STATUS\n")
            self.serial_port.flush()
            return True
        except serial.SerialException:
            return False
    
    def request_rssi(self) -> bool:
        """Solicita el RSSI del último mensaje"""
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            self.serial_port.write(b"RSSI\n")
            self.serial_port.flush()
            return True
        except serial.SerialException:
            return False
    
    def set_device_id(self, device_id: str) -> bool:
        """
        Configura el ID del dispositivo
        
        Args:
            device_id: ID en formato hexadecimal
        """
        if not self.is_connected or not self.serial_port:
            return False
        
        try:
            command = f"ID:{device_id}\n"
            self.serial_port.write(command.encode('utf-8'))
            self.serial_port.flush()
            return True
        except serial.SerialException:
            return False
    
    def _read_loop(self):
        """Loop de lectura en thread separado"""
        buffer = ""
        
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    # Leer datos disponibles
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer += data.decode('utf-8', errors='ignore')
                    
                    # Procesar líneas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if line:
                            self._process_line(line)
                
                time.sleep(0.01)  # Pequeño delay para no saturar CPU
                
            except serial.SerialException as e:
                if self.on_error:
                    self.on_error(f"Error de lectura: {str(e)}")
                break
            except Exception as e:
                if self.on_error:
                    self.on_error(f"Error inesperado: {str(e)}")
    
    def _process_line(self, line: str):
        """
        Procesa una línea recibida del ESP32
        
        Args:
            line: Línea de texto recibida
        """
        # Mensaje recibido: RX:Nombre:Mensaje:RSSI
        if line.startswith("RX:"):
            parts = line.split(':', 3)
            if len(parts) >= 4:
                sender_name = parts[1]
                message = parts[2]
                rssi = parts[3]
                
                if self.on_message_received:
                    self.on_message_received(sender_name, message, rssi)
        
        # Mensaje enviado confirmado: SENT:OK:Nombre:Mensaje
        elif line.startswith("SENT:OK:"):
            if self.on_status_update:
                self.on_status_update("Mensaje enviado correctamente")
        
        # Estado del dispositivo
        elif line.startswith("STATUS:"):
            if self.on_status_update:
                self.on_status_update(line)
        
        # RSSI
        elif line.startswith("RSSI:"):
            if self.on_status_update:
                self.on_status_update(line)
        
        # Errores
        elif line.startswith("ERROR:"):
            if self.on_error:
                self.on_error(line)
        
        # Ready
        elif line == "READY":
            if self.on_status_update:
                self.on_status_update("Dispositivo listo")
        
        # Otros mensajes informativos
        else:
            if self.on_status_update:
                self.on_status_update(line)


# Ejemplo de uso
if __name__ == "__main__":
    def on_message(sender, message, rssi):
        print(f"\n[{sender}]: {message} (RSSI: {rssi})")
    
    def on_status(status):
        print(f"[STATUS]: {status}")
    
    def on_error(error):
        print(f"[ERROR]: {error}")
    
    # Listar puertos disponibles
    ports = LoRaSerialCommunicator.list_available_ports()
    print("Puertos disponibles:", ports)
    
    if ports:
        # Crear comunicador
        comm = LoRaSerialCommunicator()
        comm.on_message_received = on_message
        comm.on_status_update = on_status
        comm.on_error = on_error
        
        # Conectar
        if comm.connect(ports[0]):
            print(f"Conectado a {ports[0]}")
            
            # Mantener vivo
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nCerrando...")
                comm.disconnect()
