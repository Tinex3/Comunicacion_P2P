# Manual de Usuario - Sistema LoRa P2P Chat

## Descripción

Sistema de comunicación peer-to-peer (P2P) utilizando tecnología LoRa que permite el intercambio de mensajes de texto entre múltiples dispositivos a través de una interfaz gráfica en Python.

## Requisitos del Sistema

### Hardware
- ESP32-S3 (Heltec Wireless Stick Lite V3)
- Módulo LoRa SX1262
- Cable USB para conexión al PC
- Antena LoRa (915 MHz)

### Software
- **Para el ESP32:**
  - PlatformIO IDE o VSCode con extensión PlatformIO
  - Python 3.7 o superior

- **Para la aplicación Python:**
  - Python 3.7+
  - Librería pySerial

## Instalación

### 1. Configurar el ESP32

#### Opción A: Usando PlatformIO en VSCode

1. Abre el proyecto en VSCode
2. Abre PlatformIO Core CLI Terminal
3. Compila y carga el código:
   ```bash
   pio run -t upload
   ```

#### Opción B: Usando PlatformIO CLI

```bash
cd Comunicacion_P2P
pio run -t upload
```

### 2. Instalar la Aplicación Python

1. Navega al directorio de la aplicación:
   ```bash
   cd python_gui
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso de la Aplicación

### Inicio Rápido

1. **Conectar el ESP32**
   - Conecta el ESP32 al puerto USB de tu computadora
   - Espera a que el sistema reconozca el dispositivo

2. **Ejecutar la aplicación**
   ```bash
   cd python_gui
   python main.py
   ```

3. **Configuración inicial**
   - Ingresa tu nombre (máximo 30 caracteres)
   - Selecciona el puerto serie correcto (COM, ttyUSB, ttyACM, etc.)
   - Haz clic en "Conectar y Comenzar"

4. **Enviar mensajes**
   - Escribe tu mensaje en el campo de texto (máximo 96 caracteres)
   - Presiona Enter o haz clic en "Enviar"

### Interfaz de Usuario

#### Pantalla de Configuración

```
┌─────────────────────────────────────┐
│   Configuración de LoRa Chat        │
├─────────────────────────────────────┤
│ Tu nombre:                          │
│ [_____________________________]     │
│                                     │
│ Puerto Serial:                      │
│ [COM3 ▼]  [🔄 Actualizar]          │
│                                     │
│     [Conectar y Comenzar]           │
│                                     │
│ Estado: X puerto(s) encontrado(s)   │
└─────────────────────────────────────┘
```

#### Pantalla de Chat

```
┌─────────────────────────────────────────────────┐
│ LoRa Chat - TuNombre    [⚙ Configuración] [●]  │
├─────────────────────────────────────────────────┤
│ Mensajes:                                       │
│ ┌─────────────────────────────────────────────┐│
│ │ [12:30:45] [SISTEMA] Sistema iniciado      ││
│ │ [12:31:00] TuNombre: Hola a todos!         ││
│ │ [12:31:15] OtroUsuario: Hola! ¿Cómo están?││
│ │ [12:31:30] TuNombre: Muy bien, gracias!    ││
│ └─────────────────────────────────────────────┘│
│                                                 │
│ Tu mensaje:                                     │
│ [___________________________________] [📤 Enviar]│
│                                          15/96  │
├─────────────────────────────────────────────────┤
│ Listo                          RSSI: -85 dBm    │
└─────────────────────────────────────────────────┘
```

## Características

### Funcionalidades Principales

1. **Comunicación P2P**
   - Envío y recepción simultánea de mensajes
   - Sin necesidad de servidor central
   - Alcance de varios kilómetros (dependiendo del entorno)

2. **Interfaz Gráfica Intuitiva**
   - Configuración simple de usuario
   - Visualización clara de mensajes
   - Indicadores de estado en tiempo real
   - Contador de caracteres

3. **Validación de Mensajes**
   - CRC16 para integridad de datos
   - Detección de errores de transmisión
   - Indicador de calidad de señal (RSSI)

4. **Configuración Persistente**
   - Guarda tu nombre de usuario
   - Recuerda el último puerto usado
   - Configuración automática al reiniciar

### Indicadores de Estado

| Indicador | Significado |
|-----------|-------------|
| ● Verde | Conectado y listo |
| RSSI: -XX dBm | Intensidad de señal recibida |
| X/96 | Caracteres usados del máximo permitido |
| [SISTEMA] | Mensaje informativo del sistema |

### Códigos de Color

- **Azul**: Tus propios mensajes
- **Naranja**: Mensajes de otros usuarios
- **Gris**: Mensajes del sistema
- **Gris claro**: Marcas de tiempo

## Solución de Problemas

### No se detecta el puerto serie

**Problema**: La aplicación no muestra puertos disponibles

**Soluciones**:
1. Verifica que el ESP32 esté conectado
2. Instala los drivers USB-Serial apropiados
3. Intenta otro cable USB
4. Haz clic en "Actualizar" para refrescar la lista

### Error al conectar

**Problema**: "No se pudo conectar al puerto"

**Soluciones**:
1. Cierra otras aplicaciones que puedan estar usando el puerto (Arduino IDE, monitor serial, etc.)
2. Desconecta y reconecta el ESP32
3. Reinicia la aplicación
4. Verifica que el código esté cargado en el ESP32

### No se envían mensajes

**Problema**: Los mensajes no se transmiten

**Soluciones**:
1. Verifica que aparezca "● Conectado" en verde
2. Revisa que el mensaje no exceda 96 caracteres
3. Comprueba la conexión de la antena LoRa
4. Verifica el estado en el monitor serial del ESP32

### No se reciben mensajes

**Problema**: No aparecen mensajes de otros dispositivos

**Soluciones**:
1. Verifica que ambos dispositivos estén en el mismo rango
2. Comprueba que las antenas estén conectadas
3. Asegúrate de que ambos dispositivos usen la misma configuración LoRa
4. Revisa el valor de RSSI (valores < -120 dBm indican señal muy débil)

### Mensajes con errores

**Problema**: Se muestran errores de CRC

**Soluciones**:
1. Acerca los dispositivos
2. Verifica que las antenas estén correctamente conectadas
3. Evita obstáculos metálicos entre los dispositivos
4. Comprueba que no haya interferencias en 915 MHz

## Comandos del Monitor Serial

Si necesitas depurar directamente desde el ESP32, puedes usar estos comandos:

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `STATUS` | Solicita estado del dispositivo | `STATUS` |
| `RSSI` | Obtiene RSSI del último mensaje | `RSSI` |
| `ID:XXXXX` | Configura el Device ID | `ID:0000000000000001` |
| `TX:Nombre:Mensaje` | Envía un mensaje | `TX:Juan:Hola mundo` |

## Configuración Avanzada

### Cambiar Parámetros LoRa

Para modificar los parámetros de comunicación LoRa, edita estas constantes en `main.cpp`:

```cpp
#define LORA_FREQUENCY 915.0      // Frecuencia en MHz
#define LORA_BANDWIDTH 125.0      // Ancho de banda en kHz
#define LORA_SPREADING_FACTOR 7   // Factor de dispersión (7-12)
#define LORA_CODING_RATE 5        // Tasa de codificación
#define LORA_TX_POWER 10          // Potencia de transmisión en dBm
```

**Nota**: Ambos dispositivos deben tener la misma configuración para comunicarse.

### Device ID Único

Cada dispositivo debe tener un ID único. Para cambiarlo, modifica esta línea en `main.cpp`:

```cpp
uint64_t DEVICE_ID = 0x0000000000000001; // Cambia este valor
```

O usa el comando serial:
```
ID:0000000000000002
```

## Alcance y Rendimiento

### Alcance Estimado

| Entorno | Alcance Aproximado |
|---------|-------------------|
| Línea de vista | 2-5 km |
| Zona urbana | 500 m - 1 km |
| Interior de edificios | 50 - 200 m |

### Factores que Afectan el Alcance

- **Positivos**: 
  - Antena de alta ganancia
  - Posición elevada
  - Línea de vista despejada
  - Mayor potencia de transmisión

- **Negativos**:
  - Obstáculos (edificios, montañas)
  - Interferencias electromagnéticas
  - Antena de baja calidad o mal conectada
  - Entorno urbano denso

## Seguridad y Privacidad

⚠️ **IMPORTANTE**: Este sistema es para uso educativo/experimental.

- Los mensajes NO están encriptados
- Cualquier dispositivo en el rango puede recibir los mensajes
- No hay autenticación de usuarios
- Para uso en producción, se recomienda implementar encriptación

## Soporte y Contacto

Para reportar problemas o sugerencias:

- **Repositorio**: Light_Weight_Formatter
- **Organización**: Tekroy-Desarrollos
- **Documentación adicional**: Ver `ARQUITECTURA.md`

## Licencia

Este proyecto es de código abierto para fines educativos.

---

**Última actualización**: Noviembre 2025  
**Versión**: 1.0
