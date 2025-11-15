"""
Módulo de comunicación serial con ESP32 LoRa
Gestiona el envío y recepción de mensajes a través del puerto serial
"""

import serial
import serial.tools.list_ports
import threading
import time
import logging
from typing import Callable, Optional, List

# Configurar logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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
        Lista todos los puertos serie disponibles (COM, ttyUSB, ttyACM, etc.)
        con información descriptiva del dispositivo
        
        Returns:
            Lista de strings en formato: "PUERTO - Descripción" (ej: "COM3 - USB Serial Port")
            o solo "PUERTO" si no hay descripción disponible
        """
        ports = serial.tools.list_ports.comports()
        port_list = []
        
        for port in sorted(ports, key=lambda x: x.device):
            # Construir descripción informativa
            if port.description and port.description != port.device:
                # Incluir fabricante si está disponible
                if port.manufacturer and port.manufacturer not in port.description:
                    desc = f"{port.device} - {port.manufacturer} - {port.description}"
                else:
                    desc = f"{port.device} - {port.description}"
            else:
                desc = port.device
            
            port_list.append(desc)
        
        return port_list
    
    @staticmethod
    def ping_port(port: str, timeout: float = 2.0) -> bool:
        """
        Envía un PING al puerto para verificar si hay un dispositivo LoRa P2P
        
        Args:
            port: Nombre del puerto (puede incluir descripción con ' - ')
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            True si el dispositivo responde con PONG:LORA_P2P, False en caso contrario
        """
        try:
            # Extraer el nombre del puerto si viene con descripción
            port_name = port.split(' - ')[0] if ' - ' in port else port
            
            # Abrir puerto temporalmente
            ser = serial.Serial(
                port=port_name,
                baudrate=115200,
                timeout=timeout,
                write_timeout=1
            )
            
            # Esperar inicialización
            time.sleep(0.5)
            
            # Limpiar buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Enviar PING
            ser.write(b"PING\n")
            ser.flush()
            
            # Esperar respuesta
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("PONG:LORA_P2P"):
                        ser.close()
                        return True
                time.sleep(0.1)
            
            ser.close()
            return False
            
        except Exception as e:
            return False
    
    @staticmethod
    def detect_lora_ports(progress_callback: Optional[Callable] = None) -> List[str]:
        """
        Detecta automáticamente los puertos con dispositivos LoRa P2P conectados
        mediante PING/PONG
        
        Args:
            progress_callback: Función opcional para reportar progreso
                              Recibe (puerto_actual, total_puertos)
        
        Returns:
            Lista de puertos que respondieron al PING (con descripción)
        """
        all_ports = LoRaSerialCommunicator.list_available_ports()
        lora_ports = []
        
        for idx, port in enumerate(all_ports):
            if progress_callback:
                progress_callback(port, idx + 1, len(all_ports))
            
            if LoRaSerialCommunicator.ping_port(port, timeout=1.5):
                lora_ports.append(port)
        
        return lora_ports
    
    def connect(self, port: str) -> bool:
        """
        Conecta al puerto serial especificado
        
        Args:
            port: Nombre del puerto (ej: 'COM3 - USB Serial' o '/dev/ttyUSB0')
                 Si contiene ' - ', se extrae solo la parte del nombre del puerto
            
        Returns:
            True si la conexión fue exitosa
        """
        try:
            # Extraer el nombre del puerto si viene con descripción
            port_name = port.split(' - ')[0] if ' - ' in port else port
            
            logger.info(f"🔌 Conectando al puerto {port_name}...")
            
            self.serial_port = serial.Serial(
                port=port_name,
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
            
            logger.info(f"✅ Conectado exitosamente a {port_name}")
            
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
        logger.info("🔌 Desconectando...")
        
        self.running = False
        
        if self.read_thread:
            self.read_thread.join(timeout=2)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.is_connected = False
        logger.info("✅ Desconectado exitosamente")
    
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
            logger.warning("⚠️  Intento de envío sin conexión activa")
            if self.on_error:
                self.on_error("No hay conexión con el dispositivo")
            return False
        
        try:
            # Formato: TX:Nombre:Mensaje\n
            command = f"TX:{sender_name}:{message}\n"
            self.serial_port.write(command.encode('utf-8'))
            self.serial_port.flush()
            logger.info(f"📡 Enviando mensaje de '{sender_name}': {message}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"❌ Error al enviar mensaje: {str(e)}")
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
                            # SIEMPRE imprimir TODO lo que viene del serial (DEBUG)
                            print(f"[SERIAL RAW] {line}")
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
                
                logger.info(f"📥 Mensaje recibido de '{sender_name}': {message} (RSSI: {rssi} dBm)")
                
                if self.on_message_received:
                    self.on_message_received(sender_name, message, rssi)
        
        # Mensaje enviado confirmado: SENT:OK:Nombre:Mensaje
        elif line.startswith("SENT:OK:"):
            parts = line.split(':', 3)
            if len(parts) >= 4:
                name = parts[2]
                msg = parts[3]
                logger.info(f"📤 Mensaje enviado exitosamente por '{name}': {msg}")
            
            if self.on_status_update:
                self.on_status_update("Mensaje enviado correctamente")
        
        # Estado del dispositivo
        elif line.startswith("STATUS:"):
            logger.info(f"ℹ️  Estado: {line}")
            if self.on_status_update:
                self.on_status_update(line)
        
        # RSSI
        elif line.startswith("RSSI:"):
            logger.debug(f"📊 {line}")
            if self.on_status_update:
                self.on_status_update(line)
        
        # Errores
        elif line.startswith("ERROR:"):
            # Identificar tipos de error específicos
            if "CRC_INVALID" in line:
                logger.error(f"❌ Error de CRC - Datos corruptos recibidos")
            elif "TX_FAILED" in line:
                logger.error(f"❌ Error de transmisión LoRa: {line}")
            elif "RX_FAILED" in line:
                logger.error(f"❌ Error de recepción LoRa: {line}")
            else:
                logger.error(f"❌ {line}")
            
            if self.on_error:
                self.on_error(line)
        
        # Ready
        elif line == "READY":
            logger.info(f"✅ Dispositivo LoRa inicializado y listo")
            if self.on_status_update:
                self.on_status_update("Dispositivo listo")
        
        # PONG response
        elif line.startswith("PONG:"):
            logger.debug(f"🏓 Respuesta PING recibida: {line}")
            if self.on_status_update:
                self.on_status_update(line)
        
        # Debug messages
        elif line.startswith("DEBUG:"):
            if "IGNORING_OWN_MESSAGE" in line:
                logger.debug(f"🔇 Mensaje propio ignorado (evitando eco)")
            elif "INVALID_MAGIC_BYTES" in line:
                logger.debug(f"🛡️ Ruido filtrado - Magic bytes inválidos (probablemente LoRaWAN u otro protocolo)")
            elif "PACKET_TOO_SHORT" in line:
                logger.debug(f"🛡️ Paquete demasiado corto ignorado")
            else:
                logger.debug(f"🐛 {line}")
            if self.on_status_update:
                self.on_status_update(line)
        
        # Otros mensajes informativos
        else:
            logger.debug(f"▪️  {line}")
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
