# 🌐 LoRa P2P Chat - Versión Web

## Aplicación Web con Docker

La versión web del sistema LoRa P2P Chat permite acceder a la interfaz desde cualquier navegador, facilitando el despliegue y uso en múltiples plataformas.

---

## 🚀 Características de la Versión Web

✅ **Interfaz Web Moderna** - HTML5 + CSS3 + JavaScript  
✅ **API REST** - FastAPI con documentación automática  
✅ **WebSockets** - Comunicación en tiempo real  
✅ **Responsive Design** - Funciona en desktop, tablet y móvil  
✅ **Docker Ready** - Despliegue fácil con contenedores  
✅ **Multi-usuario** - Varios navegadores pueden conectarse simultáneamente  
✅ **Sin instalación local** - Solo necesitas un navegador  

---

## 📋 Requisitos

### Para Ejecución Directa (Sin Docker)
- Python 3.11+
- ESP32 conectado por USB
- Navegador web moderno (Chrome, Firefox, Edge, Safari)

### Para Ejecución con Docker
- Docker Desktop instalado
- ESP32 conectado por USB
- Navegador web moderno

---

## 🔧 Instalación y Uso

### Opción 1: Ejecución Directa (Recomendado para desarrollo)

#### Windows
```bash
# Ejecutar el script de inicio
run_web.bat
```

#### Linux/Mac
```bash
# Dar permisos de ejecución
chmod +x run_web.sh

# Ejecutar
./run_web.sh
```

#### Manual
```bash
# Navegar al directorio
cd python_gui

# Instalar dependencias
pip install -r requirements-web.txt

# Iniciar servidor
python web_server.py
```

**Acceder a la aplicación:**
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- API Redoc: http://localhost:8000/redoc

---

### Opción 2: Docker (Recomendado para producción)

#### Windows
```bash
# Ejecutar script Docker
run_docker.bat
```

#### Linux/Mac
```bash
cd python_gui

# Construir y ejecutar
docker-compose up --build
```

#### Comandos Docker útiles

```bash
# Iniciar en background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache
```

**Nota Windows**: Para acceso USB en Docker Desktop en Windows, necesitas WSL2 y usbipd:
```powershell
# En PowerShell como Administrador
winget install usbipd
usbipd wsl list
usbipd wsl attach --busid <BUSID>
```

---

## 🎨 Interfaz Web

### Pantalla de Configuración

```
┌────────────────────────────────────────┐
│  📡 LoRa P2P Chat         TuNombre  ●  │
├────────────────────────────────────────┤
│                                        │
│     Configuración de Conexión         │
│                                        │
│     Tu nombre:                         │
│     [___________________________]      │
│                                        │
│     Puerto Serial:                     │
│     [COM3                    ▼]        │
│                                        │
│     [🔄 Actualizar] [Conectar]        │
│                                        │
└────────────────────────────────────────┘
```

### Pantalla de Chat

```
┌────────────────────────────────────────┐
│  📡 LoRa P2P Chat      Juan        ●   │
├────────────────────────────────────────┤
│                                        │
│  [12:30:45]                            │
│  Juan: Hola a todos!            ────┐  │
│                                        │
│  [12:31:00]                            │
│  ┌──── María: ¡Hola! ¿Cómo estás?     │
│                                        │
│  [12:31:15]                            │
│  Pedro: Todo bien, gracias      ────┐  │
│                                        │
├────────────────────────────────────────┤
│  [___________________] [📤 Enviar]     │
│                              15/96     │
├────────────────────────────────────────┤
│  Listo                  📶 -85 dBm     │
└────────────────────────────────────────┘
```

---

## 🔌 API REST

### Endpoints Disponibles

#### GET `/api/ports`
Lista puertos COM disponibles

**Respuesta:**
```json
{
  "ports": ["COM3", "COM4"]
}
```

#### POST `/api/connect`
Conecta al dispositivo LoRa

**Body:**
```json
{
  "name": "Juan",
  "port": "COM3"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Conectado exitosamente",
  "name": "Juan",
  "port": "COM3"
}
```

#### POST `/api/send`
Envía un mensaje

**Body:**
```json
{
  "sender": "Juan",
  "content": "Hola mundo"
}
```

#### GET `/api/messages`
Obtiene historial de mensajes

**Respuesta:**
```json
{
  "messages": [
    {
      "sender": "Juan",
      "content": "Hola mundo",
      "timestamp": "12:30:45",
      "is_own": true
    }
  ]
}
```

#### GET `/api/status`
Obtiene estado del sistema

**Respuesta:**
```json
{
  "connected": true,
  "port": "COM3",
  "user_name": "Juan",
  "rssi": -85,
  "messages_count": 15,
  "uptime": "0:15:30"
}
```

#### WebSocket `/ws`
Comunicación en tiempo real

**Mensajes recibidos:**
```json
{
  "type": "message",
  "data": {
    "sender": "María",
    "content": "Hola",
    "timestamp": "12:30:45",
    "rssi": "-85",
    "is_own": false
  }
}
```

---

## 🐳 Docker

### Dockerfile

La imagen Docker incluye:
- Python 3.11 slim
- Todas las dependencias Python
- Soporte para dispositivos USB
- Hot reload en desarrollo

### docker-compose.yml

Configuración:
- Puerto expuesto: 8000
- Acceso a dispositivos USB
- Volúmenes para desarrollo
- Red aislada

### Variables de Entorno

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=info
```

---

## 📱 Acceso Móvil

La aplicación web es completamente responsive:

### Desde la misma red (LAN)

1. Obtén la IP de tu PC:
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. En tu móvil/tablet, abre el navegador:
   ```
   http://192.168.1.XX:8000
   ```

### Desde Internet (con precaución)

**⚠️ Advertencia**: Solo para pruebas en redes controladas.

Usando ngrok:
```bash
# Instalar ngrok
# https://ngrok.com/download

# Exponer puerto
ngrok http 8000
```

---

## 🔒 Seguridad

### Recomendaciones

✅ **Usar HTTPS** en producción  
✅ **Autenticación** para acceso público  
✅ **Firewall** para limitar acceso  
✅ **Rate limiting** para prevenir abuso  
✅ **Validación** de entrada en servidor  

### Para Producción

Considera agregar:
- Autenticación con JWT
- HTTPS con certificados SSL
- Nginx como reverse proxy
- Rate limiting con Redis
- Logs estructurados

---

## 🛠️ Desarrollo

### Estructura de Archivos

```
python_gui/
├── web_server.py           # Backend FastAPI
├── serial_comm.py          # Comunicación serial (reutilizado)
├── static/
│   ├── index.html         # Frontend HTML
│   └── app.js             # JavaScript
├── Dockerfile             # Imagen Docker
├── docker-compose.yml     # Orquestación
├── requirements-web.txt   # Dependencias web
└── requirements.txt       # Dependencias desktop
```

### Hot Reload

El servidor se recarga automáticamente al detectar cambios:

```bash
# En desarrollo
uvicorn web_server:app --reload
```

### Debugging

Ver logs del servidor:
```bash
# Docker
docker-compose logs -f

# Directo
# Los logs aparecen en la consola
```

### Personalización

**Cambiar puerto:**
```python
# web_server.py
uvicorn.run(..., port=8080)
```

**Cambiar tema:**
```css
/* static/index.html - Sección :root */
:root {
    --primary-color: #YOUR_COLOR;
}
```

---

## 📊 Comparación: Desktop vs Web

| Característica | Desktop (Tkinter) | Web (FastAPI) |
|----------------|-------------------|---------------|
| **Instalación** | Python local | Navegador |
| **Multi-usuario** | 1 instancia | Ilimitado |
| **Acceso remoto** | No | Sí (LAN/Internet) |
| **Móvil** | No | Sí |
| **Docker** | No | Sí |
| **Recursos** | Bajo | Medio |
| **Desarrollo** | Simple | Más complejo |
| **API** | No | Sí (REST) |
| **WebSockets** | No | Sí |

---

## 🚨 Solución de Problemas

### Puerto 8000 en uso

```bash
# Windows - Encontrar proceso
netstat -ano | findstr :8000

# Terminar proceso
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Docker no detecta USB

**Windows:**
```powershell
# Instalar usbipd
winget install usbipd

# Listar dispositivos
usbipd wsl list

# Adjuntar dispositivo
usbipd wsl attach --busid X-Y
```

**Linux:**
```bash
# Verificar dispositivo
ls -l /dev/ttyUSB*

# Dar permisos
sudo chmod 666 /dev/ttyUSB0

# Agregar usuario a grupo
sudo usermod -a -G dialout $USER
```

### WebSocket no conecta

1. Verifica que el servidor esté corriendo
2. Abre consola del navegador (F12)
3. Revisa errores de conexión
4. Asegúrate de usar el protocolo correcto (ws:// o wss://)

### CORS errors

Ya configurado en el servidor, pero si persiste:

```python
# web_server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios
    ...
)
```

---

## 📚 Documentación API Interactiva

FastAPI genera documentación automática:

### Swagger UI
http://localhost:8000/docs

Características:
- Probar endpoints directamente
- Ver esquemas de datos
- Ejemplos de requests/responses

### ReDoc
http://localhost:8000/redoc

Documentación alternativa:
- Vista más limpia
- Mejor para lectura
- Exportable a PDF

---

## 🎯 Casos de Uso

### 1. Demo/Presentación
```bash
# Inicio rápido con Docker
docker-compose up
# Acceder desde cualquier dispositivo en la red
```

### 2. Desarrollo
```bash
# Con hot reload
python web_server.py
# Editar código y ver cambios inmediatamente
```

### 3. Producción
```bash
# Con Docker en servidor
docker-compose up -d
# Configurar reverse proxy (Nginx)
# Agregar HTTPS
```

### 4. Múltiples Usuarios
- Un ESP32 conectado al servidor
- Múltiples navegadores accediendo
- Todos ven los mismos mensajes en tiempo real

---

## 🔄 Actualización desde Versión Desktop

Si ya tienes la versión Tkinter:

1. Los archivos ESP32 NO cambian
2. `serial_comm.py` se reutiliza sin cambios
3. Solo se agregan archivos web nuevos

**Puedes tener ambas versiones:**
```bash
# Desktop
python main.py

# Web
python web_server.py
```

---

## 📦 Despliegue en Servidor

### Servidor Linux

```bash
# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Clonar repositorio
git clone <repo>
cd Comunicacion_P2P/python_gui

# Iniciar con Docker
docker-compose up -d

# Configurar firewall
sudo ufw allow 8000
```

### Raspberry Pi

Funciona perfectamente en RPi para crear un gateway LoRa:

```bash
# Mismo proceso que Linux
# Conectar ESP32 por USB
# Acceder desde otros dispositivos en la red
```

---

## 💡 Tips y Trucos

### Acceso desde móvil en LAN

```bash
# En el servidor
python web_server.py

# Desde móvil
http://<IP_DEL_PC>:8000
```

### Múltiples dispositivos LoRa

Puedes tener varias instancias corriendo en diferentes puertos:

```bash
# Terminal 1
uvicorn web_server:app --port 8000

# Terminal 2 (modificar puerto en código)
uvicorn web_server:app --port 8001
```

### Logs personalizados

```python
# web_server.py
import logging

logging.basicConfig(level=logging.DEBUG)
```

---

## ✅ Checklist de Implementación

- [x] Backend FastAPI con WebSockets
- [x] Frontend HTML/CSS/JS responsive
- [x] API REST completa
- [x] Dockerfile funcional
- [x] docker-compose.yml
- [x] Scripts de inicio (.bat y .sh)
- [x] Documentación completa
- [x] Reutilización de serial_comm.py
- [x] Soporte multi-usuario
- [x] Interfaz moderna y atractiva

---

**Versión Web**: 2.0  
**Autor**: Tekroy Desarrollos  
**Última actualización**: Noviembre 2025  

¡La versión web está lista para usar! 🚀🌐
