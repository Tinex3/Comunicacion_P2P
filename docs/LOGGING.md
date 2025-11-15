# Sistema de Logging - LoRa P2P Chat

## 📋 Descripción

El sistema ahora incluye logging detallado en todos los componentes para facilitar el debugging y monitoreo de la comunicación LoRa.

## 🎯 Tipos de Logs

### Logs de Conexión
- **🔌 Conectando** - Intento de conexión al puerto serial
- **✅ Conectado exitosamente** - Conexión establecida
- **🔌 Desconectando** - Inicio del proceso de desconexión
- **✅ Desconectado exitosamente** - Desconexión completada

### Logs de Mensajes
- **📡 Enviando mensaje** - Mensaje siendo transmitido vía serial
- **📥 Mensaje recibido** - Mensaje LoRa recibido con RSSI
- **📤 Mensaje enviado exitosamente** - Confirmación del ESP32

### Logs de Estado
- **ℹ️ Estado** - Actualizaciones de estado del dispositivo
- **✅ Dispositivo LoRa inicializado** - ESP32 listo para operar
- **🏓 Respuesta PING** - Respuesta PONG del dispositivo

### Logs de Errores
- **❌ Error de CRC** - Datos corruptos recibidos
- **❌ Error de transmisión LoRa** - Fallo al transmitir
- **❌ Error de recepción LoRa** - Fallo al recibir
- **⚠️ Intento de envío sin conexión** - Operación sin dispositivo conectado

### Logs de Auto-detección
- **🔍 Iniciando detección automática** - Escaneo de puertos LoRa
- **✅ Dispositivos LoRa detectados** - Lista de puertos con LoRa
- **⚠️ No se detectaron dispositivos** - Ningún puerto respondió PONG

## 🐳 Ver Logs en Docker

### Logs en Tiempo Real
```bash
docker-compose logs -f
```

### Logs del Contenedor Específico
```bash
docker logs -f lora-p2p-chat
```

### Últimas 100 Líneas
```bash
docker logs --tail 100 lora-p2p-chat
```

### Logs con Timestamps
```bash
docker logs -t lora-p2p-chat
```

## 💻 Ver Logs en Ejecución Nativa

### Windows PowerShell
```powershell
python web_server.py
# Los logs aparecen directamente en la consola
```

### Con Redirección a Archivo
```powershell
python web_server.py 2>&1 | Tee-Object -FilePath logs.txt
```

## 🧪 Probar el Sistema de Logs

### Script de Prueba
```bash
cd python_gui
python test_logs.py
```

Este script:
1. Lista puertos disponibles
2. Se conecta al puerto seleccionado
3. Envía un mensaje de prueba
4. Muestra todos los logs generados

### Monitor Serial Directo
```bash
python test_serial_monitor.py COM3
```

Muestra todos los mensajes del ESP32 en tiempo real.

## 📊 Niveles de Log

El sistema usa los siguientes niveles estándar de Python logging:

- **DEBUG** - Información detallada para debugging (RSSI, PONG)
- **INFO** - Operaciones normales (conexión, mensajes, estado)
- **WARNING** - Advertencias (puerto incorrecto, mensaje largo)
- **ERROR** - Errores que no detienen la ejecución (CRC inválido, TX failed)
- **CRITICAL** - Errores fatales (no implementado actualmente)

## 🔧 Configurar Nivel de Log

### En el Código
```python
import logging

# Ver solo errores y advertencias
logging.basicConfig(level=logging.WARNING)

# Ver todo incluyendo debug
logging.basicConfig(level=logging.DEBUG)

# Ver operaciones normales (recomendado)
logging.basicConfig(level=logging.INFO)
```

### Variable de Entorno Docker
Edita `docker-compose.yml`:
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 📝 Ejemplos de Salida

### Conexión Exitosa
```
2025-11-15 10:30:45 - serial_comm - INFO - 🔌 Conectando al puerto COM3...
2025-11-15 10:30:47 - serial_comm - INFO - ✅ Conectado exitosamente a COM3
2025-11-15 10:30:47 - serial_comm - INFO - ✅ Dispositivo LoRa inicializado y listo
```

### Envío de Mensaje
```
2025-11-15 10:31:20 - web_server - INFO - 📤 API: Solicitando envío de mensaje de 'Juan': Hola mundo
2025-11-15 10:31:20 - serial_comm - INFO - 📡 Enviando mensaje de 'Juan': Hola mundo
2025-11-15 10:31:21 - serial_comm - INFO - 📤 Mensaje enviado exitosamente por 'Juan': Hola mundo
```

### Recepción de Mensaje
```
2025-11-15 10:31:25 - serial_comm - INFO - 📥 Mensaje recibido de 'María': Hola Juan! (RSSI: -45.5 dBm)
```

### Error de CRC
```
2025-11-15 10:32:10 - serial_comm - ERROR - ❌ Error de CRC - Datos corruptos recibidos
```

### Auto-detección
```
2025-11-15 10:35:00 - web_server - INFO - 🔍 Iniciando detección automática de dispositivos LoRa...
2025-11-15 10:35:05 - web_server - INFO - ✅ Dispositivos LoRa detectados: COM3 - Silicon Labs - CP210x
```

## 🔍 Debugging de Problemas

### "No se reciben mensajes"
Busca en los logs:
```
❌ Error de CRC          → Problema de protocolo/configuración
❌ Error de recepción    → Problema de hardware LoRa
📥 Mensaje recibido      → Mensaje SÍ llega (problema en UI)
```

### "Error al conectar"
```
❌ Error de conexión: [Errno 2] → Puerto incorrecto
❌ Error de conexión: [Errno 13] → Puerto ocupado
⚠️ No se detectaron dispositivos → ESP32 no responde PING
```

### "Mensajes no llegan al otro dispositivo"
```
📡 Enviando mensaje      → Se envía desde Python
📤 Mensaje enviado OK    → ESP32 confirmó TX exitoso
📥 NO aparece en receptor → Problema LoRa (frecuencia, alcance)
```

## 📚 Archivos con Logging

- `serial_comm.py` - Comunicación serial y protocolo
- `web_server.py` - API REST y WebSockets
- `main.py` - GUI Desktop (si se implementa)

## 🎨 Emojis de Referencia Rápida

| Emoji | Significado |
|-------|-------------|
| 🔌 | Conexión |
| ✅ | Éxito |
| ❌ | Error |
| ⚠️ | Advertencia |
| 📡 | Transmisión |
| 📥 | Recepción |
| 📤 | Envío confirmado |
| 🔍 | Detección/búsqueda |
| ℹ️ | Información |
| 🏓 | PING/PONG |
| 📊 | Métricas (RSSI) |
