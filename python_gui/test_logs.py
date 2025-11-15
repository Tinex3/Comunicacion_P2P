"""
Script de prueba para verificar que los logs funcionan correctamente
"""

import logging
from serial_comm import LoRaSerialCommunicator

# Configurar logging para ver todos los niveles
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("Prueba de Sistema de Logging - LoRa P2P Chat")
    print("=" * 60)
    print()
    
    # Listar puertos disponibles
    logger.info("Listando puertos disponibles...")
    ports = LoRaSerialCommunicator.list_available_ports()
    
    if not ports:
        logger.error("No se encontraron puertos disponibles")
        return
    
    print("\nPuertos disponibles:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port}")
    
    # Seleccionar puerto
    port_idx = int(input("\nSelecciona el puerto (número): ")) - 1
    selected_port = ports[port_idx]
    
    # Crear comunicador
    logger.info("Creando comunicador...")
    comm = LoRaSerialCommunicator()
    
    # Definir callbacks
    def on_message(sender, message, rssi):
        logger.info(f"Callback: Mensaje recibido")
    
    def on_status(status):
        logger.info(f"Callback: Status update")
    
    def on_error(error):
        logger.error(f"Callback: Error detectado")
    
    comm.on_message_received = on_message
    comm.on_status_update = on_status
    comm.on_error = on_error
    
    # Conectar
    logger.info(f"Intentando conectar a {selected_port}...")
    if comm.connect(selected_port):
        logger.info("Conexión exitosa - esperando 3 segundos...")
        
        import time
        time.sleep(3)
        
        # Enviar mensaje de prueba
        name = input("\nNombre del remitente: ")
        msg = input("Mensaje de prueba: ")
        
        logger.info("Enviando mensaje de prueba...")
        comm.send_message(name, msg)
        
        # Esperar respuesta
        print("\nEsperando 5 segundos para recibir respuestas...")
        time.sleep(5)
        
        # Desconectar
        logger.info("Desconectando...")
        comm.disconnect()
        
    else:
        logger.error("No se pudo conectar al dispositivo")
    
    print("\n" + "=" * 60)
    print("Prueba completada")
    print("=" * 60)

if __name__ == "__main__":
    main()
