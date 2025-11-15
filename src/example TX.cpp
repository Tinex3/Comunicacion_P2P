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

#define ADC_CTRL GPIO_NUM_37
#define BATT_GPIO GPIO_NUM_1

float BATT_Read();
float BATT_Read(){
  digitalWrite(ADC_CTRL, LOW);
  delay(100);
  
  float f = analogRead(BATT_GPIO) * (390.0/100.0 + 1)*3.3/1024.0;
  digitalWrite(ADC_CTRL, HIGH);
  //rtc_gpio_isolate(ADC_CTRL);
  return f;
}

/* Prototipos
*/

uint8_t Send_RING(uint8_t RING_ID);

void isr_BTN_A(){
  Send_RING(0);
}
void isr_BTN_B(){
  Send_RING(1);
}
void isr_BTN_C(){
  Send_RING(2);
}

#define LED GPIO_NUM_35
#define DEBUG
//https://github.com/jgromes/RadioLib/blob/master/examples/SX126x/SX126x_Transmit/SX126x_Transmit.ino
SX1262 lora_modem = new Module(HELTEC_WIRELESS_STICK_LITE_V3_LORA_NSS_GPIO_NUMBER,
                        HELTEC_WIRELESS_STICK_LITE_V3_LORA_DIO1_GPIO_NUMBER,
                        HELTEC_WIRELESS_STICK_LITE_V3_LORA_NRESET_GPIO_NUMBER,
                        HELTEC_WIRELESS_STICK_LITE_V3_LORA_BUSY_GPIO_NUMBER
                        );     

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

APP_DATA_STRUCTURE app_data;

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

uint8_t Send_RING(uint8_t RING_ID){
  //lora_modem.transmit((uint8_t *)lora_parser.get_buffer(), lora_parser.elements()) == RADIOLIB_ERR_NONE
  app_data.RING_ID = RING_ID;
  app_data.battery_voltage = BATT_Read();
  Serial.print("Battery voltage: ");
  Serial.print(app_data.battery_voltage);
  Serial.println("V");

  LW_Formatter_Restart(&LW_Formatter);
  LW_Formatter_Add_Variable_Interface(&LW_Formatter, (uint8_t *)&iot_message_encoder.DEVICE_ID, sizeof(iot_message_encoder.DEVICE_ID));
  LW_Formatter_Add_Variable_Interface(&LW_Formatter, (uint8_t *)&iot_message_encoder.MESSAGE_SOURCE_ID, sizeof(iot_message_encoder.MESSAGE_SOURCE_ID));
  iot_message_encoder.DATA_BYTE_SIZE = LW_Formatter_Get_Elements(&LW_Formatter); //Este indice se ocupara para realizar una escritura
  LW_Formatter_Add_1_Byte_Unsigned(&LW_Formatter, iot_message_encoder.DATA_BYTE_SIZE);
  LW_DATA_INDEX = LW_Formatter_Get_Elements(&LW_Formatter); //Este indice se ocupara para realizar una escritura

  LW_Formatter_Add_Data_Starting_At_Index(&LW_Formatter, LW_DATA_INDEX, &app_data.RING_ID, sizeof(app_data));
  
  uint16_t app_data_crc = Calculate_CRC(LW_Formatter.buffer, LW_Formatter.elements, CRC_Poly);
  LW_Formatter_Add_2_Byte_Unsigned(&LW_Formatter, app_data_crc);
  digitalWrite(LED, HIGH);
  send_flag = 1;

  digitalWrite(LED, HIGH);
  if(lora_modem.transmit((uint8_t *)LW_Formatter.buffer, LW_Formatter.elements) == RADIOLIB_ERR_NONE){

  #ifdef DEBUG
  Print_Info("Msg Queued\r\n");
  LW_Formatter_Print_Contents_Hex_Raw(&LW_Formatter);
  #endif
  digitalWrite(LED, LOW);
  }
  #ifdef DEBUG
  else{
    Print_Warning("MSG not queued\r\n");
  }
  #endif
  send_flag = 0;

  return RING_ID;
}
#include "driver/rtc_io.h"

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(9600);

  rtc_gpio_pullup_en(BTN_A_PIN);
  rtc_gpio_pullup_en(BTN_B_PIN);
  rtc_gpio_pullup_en(BTN_C_PIN);

  rtc_gpio_pulldown_dis(BTN_A_PIN);
  rtc_gpio_pulldown_dis(BTN_B_PIN);
  rtc_gpio_pulldown_dis(BTN_C_PIN);

  pinMode(ADC_CTRL, OUTPUT);
  analogReadResolution(10);

  /*
  pinMode(BTN_A_PIN, INPUT_PULLUP);
  pinMode(BTN_B_PIN, INPUT_PULLUP);
  pinMode(BTN_C_PIN, INPUT_PULLUP);
*/
  if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT1) {
    uint32_t wakeup_pin = esp_sleep_get_ext1_wakeup_status();

    // Determinar qué pin despertó al ESP32 y asignar un valor numérico
    uint8_t ring_id;

    SPI.begin(9,11,10);
    SPI.setFrequency(1000000);
    int state = lora_modem.begin(915, 125, 7, 5, 0x12, 10, 8);
    
    if (state != RADIOLIB_ERR_NONE) {
      Print_Warning("Starting lora_modem failed!, Code: ");
      Serial.println(state);
    }else{
      Print_Success("lora_modem Trasnceiver Init Ok!");
      Serial.println();
      lora_modem.setDio1Action(setFlag);
    }
    delay(500);
    //Inicializa el formateador
    LW_Formatter_Init(&LW_Formatter); //Initialize the formatter

    //Por comodidad, asigno variables a los miembros del formateador
    uint8_t * decoder_buffer_pointer = LW_Formatter.buffer;
    size_t decoder_buffer_size = LW_Formatter.elements;

    //Inicializa el decodificador
    LW_Decoder_Init(&Lw_Decoder, decoder_buffer_pointer, decoder_buffer_size);

    iot_message_encoder.DEVICE_ID = 0xFFAABBCCDDEE11FF;
    iot_message_encoder.MESSAGE_SOURCE_ID = 0x0;
    iot_message_encoder.DATA_PTR = (uint8_t *)&app_data;

    LW_Formatter_Restart(&LW_Formatter);
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, (uint8_t *)&iot_message_encoder.DEVICE_ID, sizeof(iot_message_encoder.DEVICE_ID));
    LW_Formatter_Add_Variable_Interface(&LW_Formatter, (uint8_t *)&iot_message_encoder.MESSAGE_SOURCE_ID, sizeof(iot_message_encoder.MESSAGE_SOURCE_ID));
    LW_Formatter_Add_1_Byte_Unsigned(&LW_Formatter, iot_message_encoder.DATA_BYTE_SIZE);
    LW_DATA_INDEX = LW_Formatter_Get_Elements(&LW_Formatter); //Este indice se ocupara para realizar una escritura

    Print_Success("Ready TX");

    if (wakeup_pin & (1ULL << BTN_A_PIN)) {
      ring_id = Send_RING(0);
    } else if (wakeup_pin & (1ULL << BTN_B_PIN)) {
      ring_id = Send_RING(1);
    } else if (wakeup_pin & (1ULL << BTN_C_PIN)) {
      ring_id = Send_RING(2);
    } else {
      Serial.println("other...");
    }
    delay(1000);
    Serial.println("OA");
    delay(1000);
    Printf_Set_Green();
    Serial.print("Sending RING ID: ");
    Serial.println(ring_id);
    Printf_Set_Default();
  }else{
  
  }

  esp_deep_sleep_disable_rom_logging();

  //esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_SLOW_MEM, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_FAST_MEM, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_XTAL, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_VDDSDIO, ESP_PD_OPTION_OFF);
  esp_sleep_enable_ext1_wakeup((1ULL << BTN_A_PIN) | (1ULL << BTN_B_PIN) | (1ULL << BTN_C_PIN), ESP_EXT1_WAKEUP_ANY_LOW);

  lora_modem.sleep();
  
  Serial.println("Entrando en modo de sueño profundo...");
  delay(1000);

  // Entrar en modo de sueño profundo
  esp_deep_sleep_start();

}

void loop() {
  // put your main code here, to run repeatedly:       

}