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

// ===================== ESTRUCTURAS DE DATOS =====================

// Estructura para mensaje de chat
typedef struct {
    char sender_name[MAX_NAME_LENGTH];
    char message[MAX_MESSAGE_LENGTH];
} Chat_Message_Data;

// Estructura del protocolo LoRa
typedef struct {
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

// ID del dispositivo (único por dispositivo)
uint64_t DEVICE_ID = 0x0000000000000001; // Se puede configurar vía serial

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
    
    // Agregar campos del protocolo
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, 
        (uint8_t *)&tx_message.DEVICE_ID, sizeof(tx_message.DEVICE_ID));
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, 
        (uint8_t *)&tx_message.MESSAGE_SOURCE_ID, sizeof(tx_message.MESSAGE_SOURCE_ID));
    
    // Calcular y agregar tamaño de datos
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
        
        // Validar CRC
        uint16_t calc_crc = Calculate_CRC(rx_buffer, packet_length, CRC_POLY);
        
        if (calc_crc == 0) {
            // CRC válido - decodificar mensaje
            rx_message = *(Tk_IOT_LW_Message *)rx_buffer;
            
            // Extraer datos del chat (después del header de 17 bytes)
            Chat_Message_Data* received_data = (Chat_Message_Data*)&rx_buffer[17];
            
            // Obtener RSSI
            float rssi = lora_modem.getRSSI();
            
            // Enviar a Python
            Serial.print("RX:");
            Serial.print(received_data->sender_name);
            Serial.print(":");
            Serial.print(received_data->message);
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
    Serial.println("  Sistema LoRa P2P Chat v1.0");
    Serial.println("  Tekroy Desarrollos");
    Serial.println("=================================\n");
    
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
    // Procesar recepción LoRa
    if (receivedFlag) {
        receivedFlag = false;
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
            serialBuffer += c;
        }
    }
    
    // Pequeño delay para no saturar el CPU
    delay(10);
}