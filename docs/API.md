# API y Referencia Técnica

## Documentación del Código ESP32

### Funciones Principales

#### `Init_LoRa()`
```cpp
bool Init_LoRa()
```
**Descripción**: Inicializa el módulo LoRa SX1262 con los parámetros configurados.

**Retorna**: `true` si la inicialización fue exitosa, `false` en caso contrario.

**Uso**:
```cpp
if (!Init_LoRa()) {
    Serial.println("Error al inicializar LoRa");
}
```

---

#### `Send_LoRa_Message()`
```cpp
bool Send_LoRa_Message(const char* name, const char* msg)
```
**Descripción**: Envía un mensaje vía LoRa.

**Parámetros**:
- `name`: Nombre del remitente (máx 31 caracteres)
- `msg`: Mensaje a enviar (máx 95 caracteres)

**Retorna**: `true` si el mensaje se envió correctamente.

**Uso**:
```cpp
Send_LoRa_Message("Usuario", "Hola mundo");
```

---

#### `Calculate_CRC()`
```cpp
uint16_t Calculate_CRC(uint8_t *data, uint16_t length, const uint16_t poly)
```
**Descripción**: Calcula el checksum CRC16 para validación de mensajes.

**Parámetros**:
- `data`: Puntero a los datos
- `length`: Longitud de los datos en bytes
- `poly`: Polinomio CRC (típicamente 0xA001)

**Retorna**: Valor CRC16 calculado.

---

#### `Process_Serial_Command()`
```cpp
void Process_Serial_Command(String command)
```
**Descripción**: Procesa comandos recibidos por el puerto serial.

**Comandos soportados**:
- `TX:Nombre:Mensaje` - Envía un mensaje
- `STATUS` - Solicita estado
- `RSSI` - Obtiene RSSI
- `ID:XXXXX` - Configura Device ID

---

### Estructuras de Datos

#### `Chat_Message_Data`
```cpp
typedef struct {
    char sender_name[MAX_NAME_LENGTH];  // 32 bytes
    char message[MAX_MESSAGE_LENGTH];   // 96 bytes
} Chat_Message_Data;
```
**Descripción**: Estructura que contiene los datos de un mensaje de chat.

**Tamaño total**: 128 bytes

---

#### `Tk_IOT_LW_Message`
```cpp
typedef struct {
    uint64_t DEVICE_ID;           // 8 bytes - ID único del dispositivo
    uint64_t MESSAGE_SOURCE_ID;   // 8 bytes - ID del retransmisor (0 si directo)
    uint8_t DATA_BYTE_SIZE;       // 1 byte  - Tamaño de los datos
    uint8_t * DATA_PTR;           // Puntero a los datos
    uint16_t MESSAGE_CRC;         // 2 bytes - Checksum CRC16
} Tk_IOT_LW_Message;
```
**Descripción**: Estructura del protocolo de comunicación LoRa.

**Tamaño del header**: 19 bytes (sin contar DATA)

---

### Constantes Configurables

```cpp
// Hardware
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_NSS_GPIO_NUMBER 8
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_DIO1_GPIO_NUMBER 14
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_NRESET_GPIO_NUMBER 12
#define HELTEC_WIRELESS_STICK_LITE_V3_LORA_BUSY_GPIO_NUMBER 13

// Parámetros LoRa
#define LORA_FREQUENCY 915.0           // MHz - Cambiar según región
#define LORA_BANDWIDTH 125.0           // kHz - [7.8, 10.4, 15.6, 20.8, 31.25, 41.7, 62.5, 125, 250, 500]
#define LORA_SPREADING_FACTOR 7        // [6-12] Mayor = más alcance, menor velocidad
#define LORA_CODING_RATE 5             // [5-8] Mayor = más redundancia
#define LORA_SYNC_WORD 0x12            // Debe coincidir en todos los dispositivos
#define LORA_TX_POWER 10               // dBm [2-20]
#define LORA_PREAMBLE_LENGTH 8         // Símbolos

// Límites de mensaje
#define MAX_MESSAGE_LENGTH 96          // Caracteres máximos del mensaje
#define MAX_NAME_LENGTH 32             // Caracteres máximos del nombre
#define BUFFER_SIZE 128                // Tamaño del buffer
```

---

## Documentación del Código Python

### Clase `LoRaSerialCommunicator`

#### Constructor
```python
def __init__(self, baudrate: int = 115200)
```
**Descripción**: Inicializa el comunicador serial.

**Parámetros**:
- `baudrate`: Velocidad de comunicación (default: 115200)

**Uso**:
```python
comm = LoRaSerialCommunicator()
```

---

#### `list_available_ports()`
```python
@staticmethod
def list_available_ports() -> List[str]
```
**Descripción**: Lista todos los puertos COM disponibles.

**Retorna**: Lista de nombres de puertos (ej: ['COM3', 'COM4'])

**Uso**:
```python
ports = LoRaSerialCommunicator.list_available_ports()
print(f"Puertos disponibles: {ports}")
```

---

#### `connect()`
```python
def connect(self, port: str) -> bool
```
**Descripción**: Conecta al puerto serial especificado.

**Parámetros**:
- `port`: Nombre del puerto (ej: 'COM3' o '/dev/ttyUSB0')

**Retorna**: `True` si la conexión fue exitosa.

**Uso**:
```python
if comm.connect('COM3'):
    print("Conectado")
```

---

#### `send_message()`
```python
def send_message(self, sender_name: str, message: str) -> bool
```
**Descripción**: Envía un mensaje vía LoRa.

**Parámetros**:
- `sender_name`: Nombre del remitente
- `message`: Contenido del mensaje

**Retorna**: `True` si el mensaje se envió correctamente.

**Uso**:
```python
comm.send_message("Usuario", "Hola mundo")
```

---

#### Callbacks

```python
# Callback cuando se recibe un mensaje
comm.on_message_received = lambda sender, msg, rssi: print(f"{sender}: {msg}")

# Callback para actualizaciones de estado
comm.on_status_update = lambda status: print(f"Estado: {status}")

# Callback para errores
comm.on_error = lambda error: print(f"Error: {error}")
```

---

### Clase `LoRaChatGUI`

#### Constructor
```python
def __init__(self, root)
```
**Descripción**: Inicializa la interfaz gráfica completa.

**Parámetros**:
- `root`: Ventana raíz de Tkinter

**Uso**:
```python
root = tk.Tk()
app = LoRaChatGUI(root)
root.mainloop()
```

---

#### Métodos Principales

```python
# Agregar mensaje propio
def add_own_message(self, message: str)

# Agregar mensaje recibido
def add_received_message(self, sender: str, message: str, rssi: str = "")

# Agregar mensaje del sistema
def add_system_message(self, message: str)

# Enviar mensaje
def send_message(self)
```

---

## Light_Weight_Formatter API

### Inicialización

```c
void LW_Formatter_Init(Light_Weight_Formatter * formatter_instance, 
                       uint8_t * buffer, 
                       size_t buffer_size);
```

**Ejemplo**:
```c
uint8_t buffer[128];
Light_Weight_Formatter formatter;
LW_Formatter_Init(&formatter, buffer, sizeof(buffer));
```

---

### Agregar Datos

```c
// Agregar variable genérica
#define LW_Formatter_Add_Variable(formatter, var)

// Agregar tipos específicos
#define LW_Formatter_Add_1_Byte_Unsigned(formatter, var)
#define LW_Formatter_Add_2_Byte_Unsigned(formatter, var)
#define LW_Formatter_Add_4_Byte_Unsigned(formatter, var)
#define LW_Formatter_Add_Float(formatter, var)
#define LW_Formatter_Add_Str(formatter, var, size)
```

**Ejemplo**:
```c
uint8_t id = 42;
uint16_t value = 1234;
float temperature = 25.5;

LW_Formatter_Add_1_Byte_Unsigned(&formatter, id);
LW_Formatter_Add_2_Byte_Unsigned(&formatter, value);
LW_Formatter_Add_Float(&formatter, temperature);
```

---

### Utilidades

```c
// Obtener número de elementos
size_t LW_Formatter_Get_Elements(Light_Weight_Formatter * formatter_instance);

// Reiniciar formateador
void LW_Formatter_Restart(Light_Weight_Formatter * lw_decoder);

// Obtener puntero al buffer
uint8_t * LW_Formatter_Get_Buffer(Light_Weight_Formatter * formatter_instance);
```

---

## Light_Weight_Decoder API

### Inicialización

```c
void LW_Decoder_Init(Light_Weight_Decoder * lw_decoder, 
                     uint8_t * buffer, 
                     size_t buffer_size);
```

---

### Decodificar Datos

```c
// Decodificar tipos específicos
uint8_t LW_Decoder_Decode_1_Byte_Unsigned(Light_Weight_Decoder * lw_decoder);
uint16_t LW_Decoder_Decode_2_Byte_Unsigned(Light_Weight_Decoder * lw_decoder);
uint32_t LW_Decoder_Decode_4_Byte_Unsigned(Light_Weight_Decoder * lw_decoder);
float LW_Decoder_Decode_Float(Light_Weight_Decoder * lw_decoder);
char * LW_Decoder_Decode_String(Light_Weight_Decoder * lw_decoder);
```

**Ejemplo**:
```c
Light_Weight_Decoder decoder;
LW_Decoder_Init(&decoder, rx_buffer, buffer_size);

uint8_t id = LW_Decoder_Decode_1_Byte_Unsigned(&decoder);
uint16_t value = LW_Decoder_Decode_2_Byte_Unsigned(&decoder);
float temp = LW_Decoder_Decode_Float(&decoder);
```

---

## Protocolo Serial

### Formato de Comandos

#### PC → ESP32

| Comando | Formato | Ejemplo |
|---------|---------|---------|
| Enviar mensaje | `TX:Nombre:Mensaje\n` | `TX:Juan:Hola mundo\n` |
| Solicitar estado | `STATUS\n` | `STATUS\n` |
| Solicitar RSSI | `RSSI\n` | `RSSI\n` |
| Configurar ID | `ID:HEXVALUE\n` | `ID:0000000000000001\n` |

#### ESP32 → PC

| Respuesta | Formato | Ejemplo |
|-----------|---------|---------|
| Mensaje recibido | `RX:Nombre:Mensaje:RSSI\n` | `RX:Maria:Hola:-85\n` |
| Mensaje enviado | `SENT:OK:Nombre:Mensaje\n` | `SENT:OK:Juan:Hola mundo\n` |
| Estado | `STATUS:OK:ID:HEXVALUE\n` | `STATUS:OK:ID:1\n` |
| RSSI | `RSSI:VALUE\n` | `RSSI:-85\n` |
| Error | `ERROR:DESCRIPTION\n` | `ERROR:CRC_INVALID\n` |
| Listo | `READY\n` | `READY\n` |

---

## Códigos de Error

### ESP32

| Código | Descripción |
|--------|-------------|
| `ERROR:LORA_INIT:X` | Error al inicializar LoRa (X = código RadioLib) |
| `ERROR:RX_START:X` | Error al iniciar recepción |
| `ERROR:TX_FAILED:X` | Error al transmitir |
| `ERROR:CRC_INVALID` | CRC del mensaje recibido es inválido |
| `ERROR:INVALID_TX_FORMAT` | Formato de comando TX incorrecto |
| `ERROR:UNKNOWN_COMMAND` | Comando no reconocido |

### Python

| Excepción | Causa |
|-----------|-------|
| `serial.SerialException` | Error de comunicación serial |
| `FileNotFoundError` | Puerto COM no encontrado |
| `PermissionError` | Puerto COM en uso por otra aplicación |

---

## Diagrama de Estados

```
┌─────────┐
│  INICIO │
└────┬────┘
     │
     ▼
┌─────────────┐
│   INIT_HW   │ ◄─── Inicializar hardware
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  INIT_LORA  │ ◄─── Configurar módulo LoRa
└─────┬───────┘
      │
      ▼
┌─────────────┐
│    READY    │ ◄─── Modo recepción continua
└─────┬───────┘
      │
      ├──────► RX_INTERRUPT ──► PROCESS_MSG ──┐
      │                                        │
      ├──────► TX_REQUEST ────► SEND_MSG ─────┤
      │                                        │
      ├──────► SERIAL_CMD ────► PROCESS_CMD ──┤
      │                                        │
      └────────────────────────◄───────────────┘
```

---

## Mejores Prácticas

### Para Desarrollo

1. **Siempre validar CRC** antes de procesar mensajes
2. **Limitar longitud de mensajes** para evitar desbordamientos
3. **Manejar timeouts** en comunicación serial
4. **Usar callbacks** para procesamiento asíncrono
5. **Reiniciar recepción** después de cada transmisión

### Para Despliegue

1. Asignar **Device IDs únicos** a cada dispositivo
2. Configurar **potencia TX** apropiada para el alcance necesario
3. Usar **spreading factor** más alto en entornos con interferencia
4. Implementar **encriptación** para datos sensibles
5. Agregar **logs** para depuración

---

## Ejemplos de Código

### Ejemplo: Envío Simple

```cpp
// ESP32
const char* name = "Usuario";
const char* msg = "Hola mundo";
Send_LoRa_Message(name, msg);
```

```python
# Python
comm.send_message("Usuario", "Hola mundo")
```

---

### Ejemplo: Recepción con Callback

```python
def on_new_message(sender, message, rssi):
    print(f"De {sender} (RSSI: {rssi}): {message}")

comm = LoRaSerialCommunicator()
comm.on_message_received = on_new_message
comm.connect('COM3')
```

---

### Ejemplo: Formateo de Mensaje Personalizado

```cpp
// Definir estructura
typedef struct {
    uint8_t sensor_id;
    float temperature;
    float humidity;
} SensorData;

// Formatear
SensorData data = {1, 25.5, 60.0};
LW_Formatter_Add_1_Byte_Unsigned(&formatter, data.sensor_id);
LW_Formatter_Add_Float(&formatter, data.temperature);
LW_Formatter_Add_Float(&formatter, data.humidity);

// Transmitir
lora_modem.transmit(formatter.buffer, formatter.elements);
```

---

## Referencia Rápida

### Límites del Sistema

| Parámetro | Valor |
|-----------|-------|
| Nombre máximo | 31 caracteres |
| Mensaje máximo | 95 caracteres |
| Buffer total | 128 bytes |
| Baudrate serial | 115200 |
| Timeout serial | 1 segundo |

### Frecuencias LoRa por Región

| Región | Frecuencia |
|--------|------------|
| América (ej: USA) | 915 MHz |
| Europa | 868 MHz |
| Asia | 433 MHz o 923 MHz |

**Importante**: Verifica las regulaciones locales antes de usar.

---

**Última actualización**: Noviembre 2025  
**Versión API**: 1.0
