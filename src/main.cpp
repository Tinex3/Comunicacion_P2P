/**
 * @file main.cpp
 * @brief Sistema de comunicación LoRa P2P con interfaz serial para Python GUI
 * @author Tekroy Desarrollos
 * @date 2025
 */

#include <Arduino.h>
#include <RadioLib.h>
#include <Light_Weight_Decoder.h>
#include <Light_Weight_Formatter.h>

// ===================== CONFIGURACIÓN HARDWARE =====================
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_NSS_GPIO_NUMBER 8
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_DIO1_GPIO_NUMBER 14
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_NRESET_GPIO_NUMBER 12
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_BUSY_GPIO_NUMBER 13
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_SCK_GPIO_NUMBER 9

#define LED GPIO_NUM_35

// ===================== CONFIGURACIÓN LORA =====================
#define LORA_FREQUENCY 915.0      // MHz
#define LORA_BANDWIDTH 125.0      // kHz
#define LORA_SPREADING_FACTOR 7
#define LORA_CODING_RATE 5
#define LORA_SYNC_WORD 0x12
#define LORA_TX_POWER 10          // dBm
#define LORA_PREAMBLE_LENGTH 8

// ===================== CONSTANTES =====================
#define MAX_MESSAGE_LENGTH 96
#define MAX_NAME_LENGTH 32
#define SERIAL_BAUD_RATE 115200
#define BUFFER_SIZE 128
const uint16_t CRC_POLY = 0xA001;

// Magic bytes para identificar nuestro protocolo (filtrar LoRaWAN y otros)
const uint32_t PROTOCOL_MAGIC = 0x50505050;  // Patrón distintivo para nuestro protocolo P2P

// ===================== ESTRUCTURAS DE DATOS =====================

// Estructura para mensaje de chat
typedef struct {
    char sender_name[MAX_NAME_LENGTH];
    char message[MAX_MESSAGE_LENGTH];
} Chat_Message_Data;

// Estructura del protocolo LoRa con magic bytes
typedef struct {
    uint32_t magic;              // Magic bytes para filtrar ruido
    uint64_t DEVICE_ID;
    uint64_t MESSAGE_SOURCE_ID;
    uint8_t DATA_BYTE_SIZE;
    uint8_t * DATA_PTR;
    uint16_t MESSAGE_CRC;
} Tk_IOT_LW_Message;

// ===================== VARIABLES GLOBALES =====================
SX1262 lora_modem = new Module(
    HELTEC_WIRELESS_STICK_LITE_V3_LORA_NSS_GPIO_NUMBER,
    HELTEC_WIRELESS_STICK_LITE_V3_LORA_DIO1_GPIO_NUMBER,
    HELTEC_WIRELESS_STICK_LITE_V3_LORA_NRESET_GPIO_NUMBER,
    HELTEC_WIRELESS_STICK_LITE_V3_LORA_BUSY_GPIO_NUMBER
);

// Buffers
uint8_t rx_buffer[BUFFER_SIZE];
uint8_t tx_buffer[BUFFER_SIZE];
uint8_t formatter_buffer[BUFFER_SIZE];

// Instancias de codificador/decodificador
Light_Weight_Formatter LW_Formatter;
Light_Weight_Decoder LW_Decoder;

// Mensajes
Tk_IOT_LW_Message tx_message;
Tk_IOT_LW_Message rx_message;
Chat_Message_Data chat_data;

// Flags
volatile bool receivedFlag = false;
volatile bool transmitFlag = false;

// ID del dispositivo (generado aleatoriamente en cada inicio basado en MAC)
uint64_t DEVICE_ID = 0;

// Buffer para comandos serial
String serialBuffer = "";

// ===================== FUNCIONES DE UTILIDAD =====================

/**
 * @brief Callback de interrupción para recepción LoRa
 */
#if defined(ESP8266) || defined(ESP32)
ICACHE_RAM_ATTR
#endif
void setRxFlag(void) {
    receivedFlag = true;
}

/**
 * @brief Calcula CRC16 para validación de mensajes
 */
uint16_t Calculate_CRC(uint8_t *data, uint16_t length, const uint16_t poly) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc >>= 1;
                crc ^= poly;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

/**
 * @brief Genera un ID único basado en la dirección MAC del ESP32
 * @return ID único de 64 bits
 */
uint64_t Generate_Unique_ID() {
    uint8_t mac[6];
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    
    // Combinar MAC address con timestamp para máxima unicidad
    uint64_t id = 0;
    for (int i = 0; i < 6; i++) {
        id = (id << 8) | mac[i];
    }
    
    // Mezclar con millis() para añadir entropía adicional
    id ^= ((uint64_t)millis() << 16);
    
    // Asegurar que nunca sea 0
    if (id == 0) {
        id = 0x544B524F59; // "TKROY" como fallback
    }
    
    return id;
}

/**
 * @brief Imprime buffer en formato hexadecimal
 */
void Print_Hex_Buffer(uint8_t *buffer, size_t length) {
    for (size_t i = 0; i < length; i++) {
        if (buffer[i] < 0x10) Serial.print("0");
        Serial.print(buffer[i], HEX);
    }
}

/**
 * @brief Inicializa el módulo LoRa
 */
bool Init_LoRa() {
    SPI.begin(9, 11, 10);
    SPI.setFrequency(1000000);
    
    int state = lora_modem.begin(
        LORA_FREQUENCY,
        LORA_BANDWIDTH,
        LORA_SPREADING_FACTOR,
        LORA_CODING_RATE,
        LORA_SYNC_WORD,
        LORA_TX_POWER,
        LORA_PREAMBLE_LENGTH
    );
    
    if (state != RADIOLIB_ERR_NONE) {
        Serial.print("ERROR:LORA_INIT:");
        Serial.println(state);
        return false;
    }
    
    lora_modem.setDio1Action(setRxFlag);
    lora_modem.setPacketReceivedAction(setRxFlag);
    
    state = lora_modem.startReceive();
    if (state != RADIOLIB_ERR_NONE) {
        Serial.print("ERROR:RX_START:");
        Serial.println(state);
        return false;
    }
    
    Serial.println("STATUS:LORA_READY");
    return true;
}

// ===================== FUNCIONES DE TRANSMISIÓN =====================

/**
 * @brief Envía un mensaje vía LoRa
 * @param name Nombre del remitente
 * @param msg Mensaje a enviar
 * @return true si se envió correctamente
 */
bool Send_LoRa_Message(const char* name, const char* msg) {
    // Preparar datos del mensaje
    memset(&chat_data, 0, sizeof(chat_data));
    strncpy(chat_data.sender_name, name, MAX_NAME_LENGTH - 1);
    strncpy(chat_data.message, msg, MAX_MESSAGE_LENGTH - 1);
    
    // Reiniciar formateador
    LW_Formatter_Restart(&LW_Formatter);
    
    // 1. AGREGAR MAGIC BYTES (para filtrar ruido)
    tx_message.magic = PROTOCOL_MAGIC;
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, 
        (uint8_t *)&tx_message.magic, sizeof(tx_message.magic));
    
    // 2. Agregar campos del protocolo
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, 
        (uint8_t *)&tx_message.DEVICE_ID, sizeof(tx_message.DEVICE_ID));
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, 
        (uint8_t *)&tx_message.MESSAGE_SOURCE_ID, sizeof(tx_message.MESSAGE_SOURCE_ID));
    
    // 3. Calcular y agregar tamaño de datos
    tx_message.DATA_BYTE_SIZE = sizeof(chat_data);
    LW_Formatter_Add_1_Byte_Unsigned(&LW_Formatter, tx_message.DATA_BYTE_SIZE);
    
    // Agregar datos del chat
    size_t data_index = LW_Formatter_Get_Elements(&LW_Formatter);
    LW_Formatter_Add_Data_Starting_At_Index(&LW_Formatter, data_index, 
        (uint8_t *)&chat_data, sizeof(chat_data));
    
    // Calcular y agregar CRC
    uint16_t crc = Calculate_CRC(LW_Formatter.buffer, 
        LW_Formatter.elements, CRC_POLY);
    LW_Formatter_Add_2_Byte_Unsigned(&LW_Formatter, crc);
    
    // Transmitir
    digitalWrite(LED, HIGH);
    int state = lora_modem.transmit(LW_Formatter.buffer, LW_Formatter.elements);
    digitalWrite(LED, LOW);
    
    if (state == RADIOLIB_ERR_NONE) {
        Serial.print("SENT:OK:");
        Serial.print(name);
        Serial.print(":");
        Serial.println(msg);
        
        // Reiniciar recepción
        lora_modem.startReceive();
        return true;
    } else {
        Serial.print("ERROR:TX_FAILED:");
        Serial.println(state);
        lora_modem.startReceive();
        return false;
    }
}

// ===================== FUNCIONES DE RECEPCIÓN =====================

/**
 * @brief Procesa un mensaje LoRa recibido
 */
void Process_Received_Message() {
    digitalWrite(LED, HIGH);
    
    int state = lora_modem.readData(rx_buffer, 0);
    
    if (state == RADIOLIB_ERR_NONE) {
        size_t packet_length = lora_modem.getPacketLength();
        
        // Validar longitud mínima (magic(4) + device_id(8) + source_id(8) + size(1) = 21 bytes mínimo)
        if (packet_length < 25) {  // 21 + al menos algo de datos + CRC(2)
            Serial.println("DEBUG:PACKET_TOO_SHORT");
            digitalWrite(LED, LOW);
            lora_modem.startReceive();
            return;
        }
        
        // 1. VALIDAR MAGIC BYTES (filtrar ruido de LoRaWAN y otros)
        uint32_t received_magic = 0;
        memcpy(&received_magic, rx_buffer, 4);
        
        if (received_magic != PROTOCOL_MAGIC) {
            Serial.println("DEBUG:INVALID_MAGIC_BYTES:NOISE_FILTERED");
            digitalWrite(LED, LOW);
            lora_modem.startReceive();
            return;
        }
        
        // 2. Validar CRC
        uint16_t calc_crc = Calculate_CRC(rx_buffer, packet_length, CRC_POLY);
        
        if (calc_crc == 0) {
            // CRC válido - extraer campos manualmente (sin cast peligroso)
            uint64_t msg_device_id = 0;
            uint64_t msg_source_id = 0;
            
            // Extraer DEVICE_ID (bytes 4-11)
            memcpy(&msg_device_id, &rx_buffer[4], 8);
            
            // Extraer MESSAGE_SOURCE_ID (bytes 12-19)
            memcpy(&msg_source_id, &rx_buffer[12], 8);
            
            // 3. IGNORAR mensajes propios (evitar eco)
            if (msg_source_id == DEVICE_ID) {
                Serial.println("DEBUG:IGNORING_OWN_MESSAGE");
                digitalWrite(LED, LOW);
                lora_modem.startReceive();
                return;
            }
            
            // 4. Extraer datos del chat (después del header: magic(4) + IDs(16) + size(1) = 21 bytes)
            Chat_Message_Data received_data;
            memset(&received_data, 0, sizeof(received_data));
            
            // Copiar datos de manera segura
            size_t data_offset = 21;
            size_t max_copy = (packet_length - data_offset - 2); // -2 por CRC al final
            if (max_copy > sizeof(Chat_Message_Data)) {
                max_copy = sizeof(Chat_Message_Data);
            }
            memcpy(&received_data, &rx_buffer[data_offset], max_copy);
            
            // Obtener RSSI
            float rssi = lora_modem.getRSSI();
            
            // Enviar a Python
            Serial.print("RX:");
            Serial.print(received_data.sender_name);
            Serial.print(":");
            Serial.print(received_data.message);
            Serial.print(":");
            Serial.println(rssi);
            
        } else {
            Serial.println("ERROR:CRC_INVALID");
        }
    } else {
        Serial.print("ERROR:RX_FAILED:");
        Serial.println(state);
    }
    
    digitalWrite(LED, LOW);
    
    // Reiniciar recepción
    lora_modem.startReceive();
}

// ===================== PROCESAMIENTO DE COMANDOS SERIAL =====================

/**
 * @brief Procesa comandos recibidos por serial
 * @param command Comando completo recibido
 */
void Process_Serial_Command(String command) {
    command.trim();
    
    if (command.length() == 0) return;
    
    // Comando TX:Nombre:Mensaje
    if (command.startsWith("TX:")) {
        int first_colon = command.indexOf(':', 3);
        if (first_colon > 0) {
            String name = command.substring(3, first_colon);
            String message = command.substring(first_colon + 1);
            
            Send_LoRa_Message(name.c_str(), message.c_str());
        } else {
            Serial.println("ERROR:INVALID_TX_FORMAT");
        }
    }
    // Comando PING - Responde PONG para identificación automática
    else if (command == "PING") {
        Serial.println("PONG:LORA_P2P");
    }
    // Comando STATUS
    else if (command == "STATUS") {
        Serial.print("STATUS:OK:ID:");
        Serial.println((unsigned long)DEVICE_ID, HEX);
    }
    // Comando ID:XXXXXXXXXXXX
    else if (command.startsWith("ID:")) {
        String id_str = command.substring(3);
        DEVICE_ID = strtoull(id_str.c_str(), NULL, 16);
        tx_message.DEVICE_ID = DEVICE_ID;
        Serial.print("CONFIG:ID:");
        Serial.println((unsigned long)DEVICE_ID, HEX);
    }
    // Comando RSSI
    else if (command == "RSSI") {
        float rssi = lora_modem.getRSSI();
        Serial.print("RSSI:");
        Serial.println(rssi);
    }
    else {
        Serial.println("ERROR:UNKNOWN_COMMAND");
    }
}

// ===================== SETUP =====================

void setup() {
    // Inicializar LED
    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);
    
    // Inicializar serial
    Serial.begin(SERIAL_BAUD_RATE);
    delay(1000);
    
    Serial.println("\n=================================");
    Serial.println("  Sistema LoRa P2P Chat v2.0");
    Serial.println("  Tekroy Desarrollos");
    Serial.println("=================================\n");
    
    // Generar ID único basado en MAC del ESP32
    DEVICE_ID = Generate_Unique_ID();
    tx_message.DEVICE_ID = DEVICE_ID;
    tx_message.MESSAGE_SOURCE_ID = DEVICE_ID;
    
    Serial.print("DEVICE_ID: 0x");
    Serial.println((unsigned long long)DEVICE_ID, HEX);
    Serial.print("PROTOCOL_MAGIC: 0x");
    Serial.println(PROTOCOL_MAGIC, HEX);
    Serial.println();
    
    // Inicializar formateador
    LW_Formatter_Init(&LW_Formatter, formatter_buffer, BUFFER_SIZE);
    
    // Inicializar decodificador
    LW_Decoder_Init(&LW_Decoder, rx_buffer, BUFFER_SIZE);
    
    // Configurar mensaje TX
    tx_message.DEVICE_ID = DEVICE_ID;
    tx_message.MESSAGE_SOURCE_ID = 0x0;
    tx_message.DATA_PTR = (uint8_t *)&chat_data;
    
    // Inicializar LoRa
    if (!Init_LoRa()) {
        Serial.println("FATAL:LORA_INIT_FAILED");
        while (1) {
            digitalWrite(LED, HIGH);
            delay(100);
            digitalWrite(LED, LOW);
            delay(100);
        }
    }
    
    Serial.println("READY");
}

// ===================== LOOP PRINCIPAL =====================

void loop() {
    // Procesar recepción LoRa (con protección contra crashes)
    if (receivedFlag) {
        receivedFlag = false;
        
        // Deshabilitar interrupciones temporalmente para evitar re-entrada
        noInterrupts();
        bool flagCopy = receivedFlag;
        receivedFlag = false;
        interrupts();
        
        // Procesar mensaje
        Process_Received_Message();
    }
    
    // Procesar comandos serial
    while (Serial.available()) {
        char c = Serial.read();
        
        if (c == '\n' || c == '\r') {
            if (serialBuffer.length() > 0) {
                Process_Serial_Command(serialBuffer);
                serialBuffer = "";
            }
        } else {
            if (serialBuffer.length() < 200) {  // Protección contra overflow
                serialBuffer += c;
            }
        }
    }
    
    // Pequeño delay para no saturar el CPU
    delay(10);
}