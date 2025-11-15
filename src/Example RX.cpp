#include <Arduino.h>
#include <RadioLib.h>
#include <Light_Weight_Decoder.h>
#include <Light_Weight_Formatter.h>

#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_NSS_GPIO_NUMBER 8
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_DIO1_GPIO_NUMBER 14
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_NRESET_GPIO_NUMBER 12
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_BUSY_GPIO_NUMBER 13
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_SCK_GPIO_NUMBER 9

#define BTN_A_PIN GPIO_NUM_20
#define BTN_B_PIN GPIO_NUM_18
#define BTN_C_PIN GPIO_NUM_21

/* Prototipos
*/

#define LED GPIO_NUM_35
#define DEBUG
//https://github.com/jgromes/RadioLib/blob/master/examples/SX126x/SX126x_Transmit/SX126x_Transmit.ino
SX1262 lora_modem = new Module(HELTEC_WIRELESS_STICK_LITE_V3_LORA_NSS_GPIO_NUMBER,
                        HELTEC_WIRELESS_STICK_LITE_V3_LORA_DIO1_GPIO_NUMBER,
                        HELTEC_WIRELESS_STICK_LITE_V3_LORA_NRESET_GPIO_NUMBER,
                        HELTEC_WIRELESS_STICK_LITE_V3_LORA_BUSY_GPIO_NUMBER
                        );     

// this function is called when a complete packet
// is received by the module
// IMPORTANT: this function MUST be 'void' type
//            and MUST NOT have any arguments!
#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
volatile uint8_t receivedFlag ;
void setFlag(void) {
// we got a packet, set the flag
  receivedFlag = 1;
}

void Printf_Set_Default(){
  Serial.print("\033[0;0m");
}

void Printf_Set_Red(){
  Serial.print("\033[0;91m");
}

void Printf_Set_Green(){
  Serial.print("\033[0;92m");
}

void Printf_Set_Yellow(){
  Serial.print("\033[0;93m");
}

void Printf_Set_Blue(){
  Serial.print("\033[0;94m");
}

void Printf_Set_Cyan(){
  Serial.print("\033[0;96m");
}

void Printf_Set_Header_Cyan(){
  Serial.print("\033[1;96m");
}

void Printf_Set_Header_Yellow(){
  Serial.print("\033[1;93m");
}

void Print_Warning(const char * s){
  Printf_Set_Red();
  Serial.print(s);
  Printf_Set_Default();
}

void Print_Success(const char * s){
  Printf_Set_Green();
  Serial.print(s);
  Printf_Set_Default();
}

void Print_Value(const char * s){
  Printf_Set_Blue();
  Serial.print(s);
  Printf_Set_Default();
}

void Set_Print_Info(){
  Printf_Set_Yellow();
}

void Set_Print_Default(){
  Printf_Set_Default();
}

void Print_Info(const char * s){
  Printf_Set_Yellow();
  Serial.print(s);
  Printf_Set_Default();
}

uint32_t A_Delay = 200;
uint8_t A_repeats = 8;

uint32_t B_Delay = 500;
uint8_t B_repeats = 4;

uint32_t C_Delay = 1000;
uint8_t C_repeats = 4;

void beep(uint32_t pin, uint32_t del, uint8_t repeats){
  for(uint8_t i = 0; i < repeats; i++){
    digitalWrite(pin, HIGH);
    delay(del);
    digitalWrite(pin, LOW);
    delay(del);
  }
}

//  1) Define una estructura que contenga todos los datos del mensaje que enviarás/recibirás (codificar y decodificar)
typedef struct{
  uint64_t DEVICE_ID; //ID del dispositivo generador del mensaje
  uint64_t MESSAGE_SOURCE_ID;  //ID del dispositivo que transporta el mensaje, 0 si es originado del mismo dispositivo. 
                            //Si otro dispositivo está haciendo puente, entonces el ID del dispositivo puente estará aqui
  uint8_t DATA_BYTE_SIZE; //Cantidad de bytes de datos enviados
  uint8_t * DATA_PTR;
  uint16_t MESSAGE_CRC; //CRC Calculado desde el DEVICE ID hasta el ultimo dato
}Tk_IOT_LW_Message;

typedef struct{
  uint8_t RING_ID;
  float battery_voltage;
}Tk_IOT_Timbre_Data;

#define APP_DATA_STRUCTURE Tk_IOT_Timbre_Data

APP_DATA_STRUCTURE * app_data;

Tk_IOT_LW_Message iot_message_decoded; //Crea un contenedor de mensajes con la estructura donde recibirás los datos
Tk_IOT_LW_Message iot_message_encoder; //Crea un contenedor de mensajes con la estructura donde enviarás los datos

//  3) Crea el formateador o decodificador
Light_Weight_Formatter LW_Formatter;   //Crea un Formateador desde donde enviarás los datos
Light_Weight_Decoder Lw_Decoder;                //Crea un Decodificador desde donde recibirás los datos

size_t LW_DATA_INDEX = 0; //Variable que se ocupa para indicar en que indice inician los datos en el formato del mensaje Tk_IOT_LW_MESSAGE
const uint16_t CRC_Poly = 0xA001;

volatile uint8_t send_flag;

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

uint8_t buff[128];
uint8_t formatter_buff[128];

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(9600);

  delay(2000);
  SPI.begin(9,11,10);
  SPI.setFrequency(1000000);
  int state = lora_modem.begin(915, 125, 7, 5, 0x12, 10, 8);
  
  if (state != RADIOLIB_ERR_NONE) {
    Print_Warning("Starting lora_modem failed!, Code: ");
    Serial.println(state);
    while (1)yield();
  }else{
    Print_Success("lora_modem Trasnceiver Init Ok!");
    Serial.println();
  }
  lora_modem.setDio1Action(setFlag);
  lora_modem.setPacketReceivedAction(setFlag);
  lora_modem.startReceive();

  if (state == RADIOLIB_ERR_NONE) {
    Serial.println(F("Escuchando!"));
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    while (true) { delay(10); }
  }

  //Inicializa el formateador
  LW_Formatter_Init(&LW_Formatter, formatter_buff, sizeof(formatter_buff)/sizeof(formatter_buff[0])); //Initialize the formatter

  //Por comodidad, asigno variables a los miembros del formateador
  uint8_t * decoder_buffer_pointer = buff;
  size_t decoder_buffer_size = 128;

  iot_message_decoded.DATA_PTR = &buff[16];
  pinMode(LED, OUTPUT);

  pinMode(BTN_A_PIN, OUTPUT);
  pinMode(BTN_B_PIN, OUTPUT);
  pinMode(BTN_C_PIN, OUTPUT);

  Print_Success("Ready RX");
}

void loop() {
  // put your main code here, to run repeatedly:      
  if(receivedFlag) {
    // reset flag
    receivedFlag = false;
    
    int rx_state = lora_modem.readData((uint8_t *)buff, 0);

    if(rx_state == RADIOLIB_ERR_NONE){
      digitalWrite(LED, HIGH);
      size_t t = lora_modem.getPacketLength();

      uint16_t calc_crc = Calculate_CRC(buff, t, CRC_Poly);
      
      Printf_Set_Cyan();
      Serial.println("===========");

      if(calc_crc == 0){
        Printf_Set_Green();
        Serial.print("CRC: ");
        Serial.print(calc_crc, HEX);
        Serial.println(" Internal CRC OK");
        Printf_Set_Default();
      }else{
        Printf_Set_Red();
        Serial.print("CRC: ");
        Serial.print(calc_crc, HEX);
        Serial.println(" CRC MISMATCH");
        Printf_Set_Default();
      }

      Printf_Set_Yellow();
      Serial.print("RX Bytes: ");
      Serial.println(t);
      for(size_t i = 0; i < t; i++){
          //printf("%02X", decoder_instance->buffer[decoder_instance->read_pointer - 1 - i]);
          char auxbuff[3];
          sprintf(auxbuff, "%02X", buff[i]);
          Serial.print(auxbuff);
      }
      Serial.println();

      iot_message_decoded = *(Tk_IOT_LW_Message *)buff;
      float rssi = lora_modem.getRSSI();
      Printf_Set_Yellow();
      Serial.println("Data: ");
      Serial.print("DEVICE ID: ");
      Serial.println(iot_message_decoded.DEVICE_ID,HEX);
      Serial.print("SOURCE ID: ");
      Serial.println(iot_message_decoded.MESSAGE_SOURCE_ID,HEX);
      Serial.print("DATA BYTES: ");
      Serial.println(iot_message_decoded.DATA_BYTE_SIZE,HEX);
      app_data = (Tk_IOT_Timbre_Data*)&buff[17];
      
      Printf_Set_Green();
      Serial.print("Ring ID: ");
      Serial.println(app_data->RING_ID);

      Printf_Set_Yellow();
      #ifdef DEBUG
      Serial.print("Device Battery: ");
      Serial.println(app_data->battery_voltage);
      Serial.print("RSSI ");
      Serial.println(rssi);
      #endif
      Printf_Set_Default();

      switch (app_data->RING_ID)
      {
      case 0:
        beep(BTN_A_PIN, A_Delay, A_repeats);
        break;
      case 1:
        beep(BTN_B_PIN, B_Delay, B_repeats);
        break;
      case 2:
        beep(BTN_C_PIN, C_Delay, C_repeats);
        break;
      
      default:
        break;
      }

      digitalWrite(LED, LOW);
      }else{
        Printf_Set_Red();
        Serial.print("Error: ");
        Serial.print(rx_state);
        Printf_Set_Default();
      }
    }
  }