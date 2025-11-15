# Sistema LoRa P2P Chat

Sistema completo de comunicación punto a punto usando tecnología LoRa con interfaz gráfica en Python.

## 📋 Descripción

Este proyecto implementa un sistema de chat inalámbrico de largo alcance usando módulos LoRa (SX1262) conectados a ESP32-S3. Los usuarios pueden enviar y recibir mensajes de texto a través de una interfaz gráfica.

**🆕 VERSIÓN WEB DISPONIBLE**: Ahora con interfaz web moderna, API REST y soporte Docker. Ver [Web Version](#-versión-web-nueva)

### Características Principales

✅ Comunicación LoRa de largo alcance (hasta 5 km en línea de vista)  
✅ **Dos interfaces**: Desktop (Tkinter) y Web (HTML5)  
✅ **API REST** con FastAPI y WebSockets  
✅ **Docker Ready** para despliegue fácil  
✅ Soporte para múltiples dispositivos simultáneos  
✅ Validación de mensajes con CRC16  
✅ Indicador de calidad de señal (RSSI)  
✅ Configuración persistente  
✅ Formato de mensaje: `Nombre: Mensaje`  

## 🚀 Inicio Rápido

### Requisitos Previos

- **Hardware**: ESP32-S3 con módulo LoRa SX1262 (Heltec Wireless Stick Lite V3)
- **Software**: 
  - PlatformIO (para compilar código ESP32)
  - Python 3.7+ (para GUI Desktop)
  - Docker (opcional, para versión Web)

### Instalación en 3 Pasos

1. **Cargar código en ESP32**
   ```bash
   cd Comunicacion_P2P
   pio run -t upload
   ```

2. **Instalar dependencias Python**
   ```bash
   cd python_gui
   
   # Para versión Desktop
   pip install -r requirements.txt
   
   # Para versión Web
   pip install -r requirements-web.txt
   ```

3. **Ejecutar la aplicación**
   
   **Desktop (Tkinter):**
   ```bash
   python main.py
   # o usar: run_chat.bat (Windows) / run_chat.sh (Linux/Mac)
   ```
   
   **Web (Navegador):**
   ```bash
   python web_server.py
   # o usar: run_web.bat (Windows) / run_web.sh (Linux/Mac)
   # Acceder a: http://localhost:8000
   ```
   
   **Docker:**
   ```bash
   docker-compose up
   # Acceder a: http://localhost:8000
   ```

## 📁 Estructura del Proyecto

```
Comunicacion_P2P/
├── platformio.ini              # Configuración PlatformIO
├── run_chat.bat/.sh           # Launchers GUI Desktop
├── run_web.bat/.sh            # Launchers GUI Web
├── run_docker.bat             # Launcher Docker
├── src/
│   ├── main.cpp               # Código principal ESP32 (TX/RX LoRa)
│   ├── example TX.cpp         # Ejemplo de transmisión (referencia)
│   └── Example RX.cpp         # Ejemplo de recepción (referencia)
├── include/
│   ├── Light_Weight_Formatter/ # Codificador de mensajes
│   └── Light_Weight_Decoder/   # Decodificador de mensajes
├── python_gui/
│   ├── main.py                # 🖥️ GUI Desktop (Tkinter)
│   ├── web_server.py          # 🌐 Backend Web (FastAPI)
│   ├── serial_comm.py         # Módulo de comunicación serial (compartido)
│   ├── static/
│   │   ├── index.html        # Frontend Web
│   │   └── app.js            # JavaScript cliente
│   ├── Dockerfile            # Imagen Docker
│   ├── docker-compose.yml    # Orquestación Docker
│   ├── requirements.txt      # Dependencias Desktop
│   └── requirements-web.txt  # Dependencias Web
└── docs/
    ├── README.md              # Este archivo
    ├── WEB_VERSION.md         # 🆕 Documentación versión Web
    ├── ARQUITECTURA.md        # Diseño del sistema
    ├── MANUAL_USUARIO.md      # Guía completa
    └── API.md                 # Referencia técnica
```

## 🖥️ vs 🌐 ¿Qué versión usar?

| Característica | Desktop (Tkinter) | Web (FastAPI) |
|----------------|-------------------|---------------|
| **Instalación** | `pip install` | `pip install` o Docker |
| **Interfaz** | Ventana nativa | Navegador web |
| **Multiplataforma** | Windows/Linux/Mac | Cualquier dispositivo con navegador |
| **Comunicación tiempo real** | ✅ Threading | ✅ WebSockets |
| **Acceso remoto** | ❌ Solo local | ✅ Posible desde red |
| **Deploy** | Ejecutable local | Servidor web / Docker |
| **Ideal para** | Uso personal/escritorio | Acceso multi-dispositivo, producción |

📖 **Documentación completa versión Web**: [`WEB_VERSION.md`](docs/WEB_VERSION.md)

---

## 🔧 Uso Básico

### En la Interfaz Gráfica

1. **Primera vez**: Ingresa tu nombre y selecciona el puerto COM
2. **Escribir mensaje**: Escribe en el campo de texto (máx 96 caracteres)
3. **Enviar**: Presiona Enter o clic en "Enviar"
4. **Recibir**: Los mensajes aparecen automáticamente

### Formato de Mensajes

Los mensajes se muestran con el formato:
```
[12:30:45] Nombre: Mensaje
```

## 📡 Especificaciones Técnicas

### Parámetros LoRa

| Parámetro | Valor |
|-----------|-------|
| Frecuencia | 915 MHz |
| Ancho de banda | 125 kHz |
| Spreading Factor | 7 |
| Coding Rate | 5 |
| Potencia TX | 10 dBm |
| Sync Word | 0x12 |

### Protocolo de Comunicación

```
[8 bytes]    [8 bytes]          [1 byte]      [N bytes]  [2 bytes]
DEVICE_ID    MESSAGE_SOURCE_ID  DATA_SIZE     DATA       CRC16
```

### Comandos Serial (PC ↔ ESP32)

| Comando | Formato | Descripción |
|---------|---------|-------------|
| Enviar mensaje | `TX:Nombre:Mensaje\n` | Transmite un mensaje |
| Mensaje recibido | `RX:Nombre:Mensaje:RSSI\n` | Notifica mensaje recibido |
| Estado | `STATUS\n` | Solicita estado del dispositivo |
| RSSI | `RSSI\n` | Obtiene intensidad de señal |

## 📚 Documentación Detallada

### Guías Disponibles

1. **[ARQUITECTURA.md](docs/ARQUITECTURA.md)**: 
   - Diseño del sistema completo
   - Diagramas de componentes y flujo de datos
   - Detalles técnicos de implementación

2. **[MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md)**:
   - Guía paso a paso de instalación
   - Uso detallado de la interfaz
   - Solución de problemas comunes
   - Configuración avanzada

## 🛠️ Desarrollo

### Compilar para ESP32

```bash
# Compilar sin cargar
pio run

# Compilar y cargar
pio run -t upload

# Monitor serial
pio device monitor
```

### Modificar Parámetros LoRa

Edita las constantes en `src/main.cpp`:

```cpp
#define LORA_FREQUENCY 915.0
#define LORA_BANDWIDTH 125.0
#define LORA_SPREADING_FACTOR 7
// ... más parámetros
```

### Ejecutar GUI en Modo Debug

```python
cd python_gui
python main.py
```

## 🔍 Resolución de Problemas

### Problema: No se detecta el puerto COM
- ✅ Verifica la conexión USB
- ✅ Instala drivers CH340/CP2102
- ✅ Haz clic en "Actualizar" en la GUI

### Problema: No se envían mensajes
- ✅ Verifica conexión de antena
- ✅ Comprueba que el LED parpadee al enviar
- ✅ Revisa monitor serial del ESP32

### Problema: CRC inválido
- ✅ Acerca los dispositivos
- ✅ Verifica antenas
- ✅ Comprueba que ambos usen la misma configuración

Ver más en [MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md#solución-de-problemas)

## 📊 Alcance Esperado

| Entorno | Alcance |
|---------|---------|
| Línea de vista | 2-5 km |
| Zona urbana | 500 m - 1 km |
| Interior | 50 - 200 m |

## ⚙️ Tecnologías Utilizadas

- **Hardware**: ESP32-S3, SX1262 LoRa
- **Framework Embebido**: Arduino, PlatformIO
- **Librería LoRa**: RadioLib v7.1.0
- **Lenguaje GUI**: Python 3.x
- **Framework GUI**: Tkinter
- **Comunicación Serial**: pySerial

## 🔐 Seguridad

⚠️ **IMPORTANTE**: Este sistema es para uso educativo/experimental.

- Los mensajes NO están encriptados
- Cualquier dispositivo puede interceptar mensajes
- No hay autenticación de usuarios
- NO usar para información sensible

## 🤝 Contribuciones

Este es un proyecto educativo. Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📝 Tareas Implementadas

- [x] ✅ Diseño de arquitectura del sistema
- [x] ✅ Código LoRa TX/RX unificado en ESP32
- [x] ✅ Adaptación de Light_Weight_Formatter/Decoder
- [x] ✅ Interfaz gráfica Python con Tkinter
- [x] ✅ Módulo de comunicación serial
- [x] ✅ Documentación completa
- [x] ✅ Manual de usuario
- [x] ✅ Sistema integrado y funcional

## 📞 Soporte

- **Organización**: Tekroy-Desarrollos
- **Repositorio**: Light_Weight_Formatter
- **Documentación**: Ver carpeta `/docs`

## 📄 Licencia

Proyecto de código abierto para fines educativos.

---

**Desarrollado por Tekroy Desarrollos**  
**Versión**: 1.0  
**Fecha**: Noviembre 2025

## 🎯 Próximos Pasos

Para comenzar a usar el sistema:

1. Lee el [Manual de Usuario](docs/MANUAL_USUARIO.md)
2. Revisa la [Arquitectura](docs/ARQUITECTURA.md) si quieres entender el funcionamiento interno
3. Carga el código en tu ESP32
4. Ejecuta la GUI en Python
5. ¡Comienza a chatear!

---

¿Necesitas ayuda? Consulta la sección de **Solución de Problemas** en el manual de usuario.
