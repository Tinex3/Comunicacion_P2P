# 🚀 GUÍA DE INICIO RÁPIDO

## Sistema LoRa P2P Chat - Configuración en 5 Minutos

---

## ⚡ Inicio Super Rápido

### Para usuarios impacientes:

**Windows**:
```cmd
1. Conecta el ESP32 al USB
2. Doble clic en: run_chat.bat
3. Ingresa tu nombre
4. Selecciona el puerto COM
5. ¡Listo para chatear!
```

**Linux/Mac**:
```bash
chmod +x run_chat.sh
./run_chat.sh
```

---

## 📋 Requisitos Mínimos

- ✅ ESP32-S3 con LoRa (Heltec Wireless Stick Lite V3)
- ✅ Python 3.7+ instalado
- ✅ Cable USB
- ✅ 5 minutos de tu tiempo

---

## 🔧 Instalación Completa

### Paso 1: Cargar Código en ESP32

**Opción A - PlatformIO (Recomendado)**
```bash
cd Comunicacion_P2P
pio run -t upload
```

**Opción B - Arduino IDE**
1. Abre `src/main.cpp` en Arduino IDE
2. Configura la placa: ESP32S3 Dev Module
3. Selecciona el puerto COM
4. Clic en "Subir"

### Paso 2: Instalar Python (si no lo tienes)

**Windows**:
- Descarga desde: https://www.python.org/downloads/
- ✅ Marca "Add Python to PATH" durante instalación

**Linux**:
```bash
sudo apt-get install python3 python3-pip
```

**Mac**:
```bash
brew install python3
```

### Paso 3: Instalar Dependencias

```bash
cd python_gui
pip install -r requirements.txt
```

O simplemente:
```bash
pip install pyserial
```

### Paso 4: Ejecutar

**Opción 1 - Scripts automáticos**:
```bash
# Windows
run_chat.bat

# Linux/Mac
./run_chat.sh
```

**Opción 2 - Manual**:
```bash
cd python_gui
python main.py
```

---

## 🎮 Uso Básico

### Primera Vez

1. **Iniciar aplicación**
   - Ejecuta `run_chat.bat` (Windows) o `run_chat.sh` (Linux/Mac)
   
2. **Configurar nombre**
   ```
   Tu nombre: [Juan___________]
   ```
   - Escribe tu nombre (máx 30 caracteres)
   
3. **Seleccionar puerto**
   ```
   Puerto Serial: [COM3 ▼] [🔄 Actualizar]
   ```
   - Selecciona el puerto donde está el ESP32
   - Clic en "Actualizar" si no aparece
   
4. **Conectar**
   - Clic en "Conectar y Comenzar"
   - Espera mensaje: "● Conectado"

### Enviar Mensaje

```
Tu mensaje: [Hola a todos!_______] [📤 Enviar]
```

1. Escribe tu mensaje (máx 96 caracteres)
2. Presiona **Enter** o clic en **Enviar**
3. Tu mensaje aparecerá en azul

### Ver Mensajes Recibidos

Los mensajes de otros aparecen automáticamente en naranja:

```
[12:30:45] Tú: Hola a todos!
[12:31:00] María: Hola Juan! ¿Cómo estás?
[12:31:15] Tú: Muy bien, gracias!
```

---

## 🔍 Solución Rápida de Problemas

### ❌ No aparece el puerto COM

**Solución**:
1. Desconecta y reconecta el USB
2. Clic en "🔄 Actualizar"
3. Instala drivers: CH340 o CP2102
4. Cierra Arduino IDE si está abierto

### ❌ Error al conectar

**Solución**:
1. Verifica que el ESP32 tenga el código cargado
2. Cierra otras aplicaciones que usen el puerto
3. Cambia de cable USB
4. Reinicia el ESP32

### ❌ No se envían mensajes

**Solución**:
1. Verifica que aparezca "● Conectado" en verde
2. Comprueba que la antena esté conectada
3. Verifica que el mensaje no exceda 96 caracteres
4. Revisa el LED del ESP32 (debe parpadear al enviar)

### ❌ No se reciben mensajes

**Solución**:
1. Acerca los dispositivos (< 10 metros para pruebas)
2. Verifica que ambos tengan antenas conectadas
3. Comprueba el RSSI (debe ser > -120 dBm)
4. Asegúrate que ambos usen la misma configuración

---

## 📊 Verificar que Funciona

### Test de Transmisión

1. Conecta el ESP32
2. Inicia la GUI
3. Envía un mensaje
4. El LED del ESP32 debe parpadear
5. Debe aparecer "SENT:OK" en la consola

### Test de Recepción (con 2 dispositivos)

1. Conecta 2 ESP32 (Dispositivo A y B)
2. Inicia 2 instancias de la GUI
3. Configura nombres diferentes
4. Envía mensaje desde A
5. Debe aparecer en B

---

## 🎯 Comandos Útiles

### Monitor Serial (Debug)

Para ver qué pasa internamente:

```bash
# PlatformIO
pio device monitor

# Arduino IDE
Herramientas > Monitor Serie (115200 baud)
```

### Comandos Manuales

Puedes escribir directamente en el monitor serial:

```
STATUS          → Ver estado del dispositivo
RSSI            → Ver intensidad de señal
TX:Nombre:Msg   → Enviar mensaje manualmente
ID:0000001      → Cambiar Device ID
```

---

## 📱 Configuración Multi-Dispositivo

### Dispositivo 1
```
Nombre: Juan
Puerto: COM3
Device ID: 0x0000000000000001 (default)
```

### Dispositivo 2
```
Nombre: María
Puerto: COM4
Device ID: 0x0000000000000002
```

### Dispositivo 3
```
Nombre: Pedro
Puerto: COM5
Device ID: 0x0000000000000003
```

**Importante**: Cada ESP32 debe tener un ID único.

---

## ⚙️ Configuración Avanzada

### Cambiar Frecuencia LoRa

Edita en `src/main.cpp`:

```cpp
#define LORA_FREQUENCY 915.0  // USA: 915, Europa: 868, Asia: 433/923
```

### Aumentar Alcance

Edita en `src/main.cpp`:

```cpp
#define LORA_SPREADING_FACTOR 12  // Más alcance (más lento)
#define LORA_TX_POWER 20          // Máxima potencia
```

### Cambiar Velocidad

```cpp
#define LORA_SPREADING_FACTOR 6   // Más rápido (menos alcance)
#define LORA_BANDWIDTH 500.0      // Mayor ancho de banda
```

---

## 📁 Archivos Importantes

```
Comunicacion_P2P/
├── run_chat.bat           ← Ejecutar (Windows)
├── run_chat.sh            ← Ejecutar (Linux/Mac)
├── README.md              ← Info general
├── src/main.cpp           ← Código ESP32
└── python_gui/
    ├── main.py            ← GUI
    ├── serial_comm.py     ← Comunicación
    └── requirements.txt   ← Dependencias
```

---

## 🆘 Ayuda Adicional

### Documentación Completa

- **Usuario**: `docs/MANUAL_USUARIO.md` → Guía detallada
- **Técnica**: `docs/ARQUITECTURA.md` → Cómo funciona
- **API**: `docs/API.md` → Referencia de código
- **Resumen**: `docs/RESUMEN_PROYECTO.md` → Vista general

### ¿Aún con problemas?

1. Lee el **Manual de Usuario** completo
2. Verifica la sección **Solución de Problemas**
3. Revisa la **API** para detalles técnicos

---

## ✅ Checklist Pre-Uso

Antes de empezar, verifica:

- [ ] ESP32 conectado al USB
- [ ] Código cargado en ESP32
- [ ] Antena LoRa conectada
- [ ] Python 3.7+ instalado
- [ ] pySerial instalado (`pip install pyserial`)
- [ ] Puerto COM libre (no usado por otra app)
- [ ] Otro dispositivo LoRa disponible para pruebas

---

## 🎉 ¡Listo!

Si todo está OK, deberías ver:

```
┌─────────────────────────────────────┐
│ LoRa Chat - TuNombre    [●]         │
├─────────────────────────────────────┤
│ Mensajes:                           │
│ [12:30:45] [SISTEMA] Sistema listo  │
│                                     │
│ Tu mensaje:                         │
│ [___________________] [📤 Enviar]  │
└─────────────────────────────────────┘
```

**¡A chatear con LoRa!** 📡🎉

---

**Tiempo estimado de setup**: 5-10 minutos  
**Dificultad**: ⭐⭐☆☆☆ (Fácil)  
**Alcance**: Hasta 5 km en línea de vista 📡

---

Para más información, consulta: `docs/MANUAL_USUARIO.md`
