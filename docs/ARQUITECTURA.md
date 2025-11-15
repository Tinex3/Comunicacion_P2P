# Arquitectura del Sistema de Comunicación LoRa P2P

## Visión General

Sistema de comunicación punto a punto (P2P) usando tecnología LoRa para múltiples dispositivos con interfaz gráfica en Python.

## Componentes Principales

### 1. Hardware (ESP32 + LoRa)
- **Microcontrolador**: ESP32-S3
- **Módulo LoRa**: SX1262 (Heltec Wireless Stick Lite V3)
- **Frecuencia**: 915 MHz
- **Parámetros LoRa**:
  - Ancho de banda: 125 kHz
  - Spreading Factor: 7
  - Coding Rate: 5
  - Sync Word: 0x12
  - Potencia TX: 10 dBm
  - Preámbulo: 8 símbolos

### 2. Software Embebido (C/C++)
- **Framework**: Arduino con PlatformIO
- **Librería LoRa**: RadioLib v7.1.0
- **Funciones principales**:
  - Transmisión/Recepción LoRa simultánea
  - Codificación/Decodificación de mensajes
  - Comunicación serial con PC
  - Validación CRC

### 3. Aplicación de Escritorio (Python)
- **GUI Framework**: Tkinter
- **Comunicación Serial**: pySerial
- **Funciones**:
  - Configuración de nombre de usuario
  - Envío de mensajes
  - Visualización de mensajes recibidos
  - Gestión de puerto serial

## Protocolo de Comunicación

### Estructura del Mensaje LoRa

```
+------------------+---------------------+------------------+------------------+--------------+
| DEVICE_ID        | MESSAGE_SOURCE_ID   | DATA_BYTE_SIZE   | DATA             | CRC16        |
| (8 bytes)        | (8 bytes)           | (1 byte)         | (N bytes)        | (2 bytes)    |
+------------------+---------------------+------------------+------------------+--------------+
```

#### Campos:
1. **DEVICE_ID** (uint64_t): Identificador único del dispositivo emisor
2. **MESSAGE_SOURCE_ID** (uint64_t): ID del dispositivo que retransmite (0 si es directo)
3. **DATA_BYTE_SIZE** (uint8_t): Tamaño de los datos en bytes
4. **DATA**: Payload del mensaje (formato: "Nombre: Mensaje")
5. **CRC16**: Checksum para validación de integridad

### Formato de Datos de Aplicación

```c
typedef struct {
    char sender_name[32];    // Nombre del remitente
    char message[96];        // Contenido del mensaje
} Chat_Message_Data;
```

**Formato de visualización**: `Nombre: Mensaje`

### Protocolo Serial PC ↔ ESP32

#### De PC a ESP32 (envío de mensaje):
```
TX:Nombre:Mensaje\n
```

#### De ESP32 a PC (recepción de mensaje):
```
RX:Nombre:Mensaje:RSSI\n
```

#### Comandos especiales:
```
STATUS\n          -> Solicitar estado del dispositivo
RSSI\n            -> Obtener RSSI del último mensaje
ID:XXXXXXXXXXXX\n -> Configurar DEVICE_ID
```

## Flujo de Datos

### Envío de Mensaje

```
Usuario escribe mensaje en GUI
        ↓
GUI envía por serial: "TX:Nombre:Mensaje\n"
        ↓
ESP32 recibe y parsea datos
        ↓
Light_Weight_Formatter codifica mensaje
        ↓
Calcula CRC16
        ↓
Transmisión LoRa
        ↓
Confirmación a GUI: "SENT:OK\n"
```

### Recepción de Mensaje

```
Módulo LoRa recibe paquete (interrupción)
        ↓
ESP32 lee datos del buffer LoRa
        ↓
Valida CRC16
        ↓
Light_Weight_Decoder decodifica mensaje
        ↓
Extrae Nombre y Mensaje
        ↓
Envía por serial: "RX:Nombre:Mensaje:RSSI\n"
        ↓
GUI parsea y muestra en pantalla
```

## Estructura de Directorios del Proyecto

```
Comunicacion_P2P/
├── platformio.ini           # Configuración PlatformIO
├── include/
│   ├── Light_Weight_Formatter/
│   │   ├── Light_Weight_Formatter.h
│   │   ├── Light_Weight_Formatter.c
│   │   └── README.md
│   └── Light_Weight_Decoder/
│       ├── Light_Weight_Decoder.h
│       ├── Light_Weight_Decoder.c
│       └── README.md
├── src/
│   └── main.cpp             # Código principal ESP32
├── python_gui/
│   ├── main.py              # Aplicación GUI principal
│   ├── serial_comm.py       # Módulo comunicación serial
│   ├── lora_protocol.py     # Parseo de protocolo
│   └── requirements.txt     # Dependencias Python
└── docs/
    ├── ARQUITECTURA.md      # Este documento
    ├── MANUAL_USUARIO.md    # Guía de uso
    └── API.md               # Documentación de funciones
```

## Consideraciones de Diseño

### Seguridad
- CRC16 para integridad de mensajes
- Validación de tamaño de mensaje (máx 128 bytes)
- Timeout en comunicación serial

### Rendimiento
- Modo recepción continua con interrupciones
- Buffer circular para múltiples mensajes
- Transmisión asíncrona

### Escalabilidad
- Soporte para múltiples dispositivos (DEVICE_ID único)
- Posibilidad de retransmisión (MESSAGE_SOURCE_ID)
- Protocolo extensible

### Compatibilidad
- Python 3.7+
- ESP32-S3
- Compatible con Windows, Linux, macOS

## Diagramas

### Diagrama de Componentes

```
┌─────────────────────────────────────┐
│         Aplicación Python           │
│  ┌─────────────────────────────┐   │
│  │    GUI (Tkinter)            │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │  Módulo Serial (pySerial)   │   │
│  └──────────┬──────────────────┘   │
└─────────────┼───────────────────────┘
              │ USB Serial
┌─────────────▼───────────────────────┐
│         ESP32-S3                    │
│  ┌──────────────────────────────┐  │
│  │  Serial Handler              │  │
│  └──────┬──────────────┬────────┘  │
│         │              │            │
│  ┌──────▼──────┐ ┌────▼────────┐  │
│  │ TX Handler  │ │ RX Handler  │  │
│  └──────┬──────┘ └────┬────────┘  │
│         │              │            │
│  ┌──────▼──────────────▼────────┐  │
│  │ Light_Weight_Formatter/      │  │
│  │ Decoder                      │  │
│  └──────────────┬───────────────┘  │
│                 │                   │
│  ┌──────────────▼───────────────┐  │
│  │  RadioLib (SX1262)           │  │
│  └──────────────┬───────────────┘  │
└─────────────────┼───────────────────┘
                  │ LoRa RF
┌─────────────────▼───────────────────┐
│      Otros Dispositivos LoRa        │
└─────────────────────────────────────┘
```

## Resumen de Tecnologías

| Componente | Tecnología |
|------------|------------|
| Hardware | ESP32-S3, SX1262 |
| Framework Embebido | Arduino, PlatformIO |
| Librería LoRa | RadioLib |
| Lenguaje GUI | Python 3.x |
| Framework GUI | Tkinter |
| Comunicación Serial | pySerial |
| Control de Versiones | Git |
| Codificación | Light_Weight_Formatter/Decoder |

## Próximos Pasos

1. ✅ Documentar arquitectura
2. ⏳ Implementar código ESP32 unificado
3. ⏳ Adaptar formatter/decoder
4. ⏳ Desarrollar GUI Python
5. ⏳ Integrar sistema completo
6. ⏳ Realizar pruebas de campo
