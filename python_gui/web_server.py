"""
Backend Web para Sistema LoRa P2P Chat
API REST con FastAPI y WebSockets para comunicación en tiempo real
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
from datetime import datetime
import os
import sys
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar el comunicador serial existente
sys.path.append(os.path.dirname(__file__))
from serial_comm import LoRaSerialCommunicator

# ===================== CONFIGURACIÓN =====================

app = FastAPI(
    title="LoRa P2P Chat API",
    description="API REST para comunicación LoRa con múltiples dispositivos",
    version="2.0.0"
)

# CORS para permitir acceso desde navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== MODELOS DE DATOS =====================

class UserConfig(BaseModel):
    name: str
    port: str

class Message(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None

class ConnectionStatus(BaseModel):
    connected: bool
    port: Optional[str] = None
    device_id: Optional[str] = None

class SystemStatus(BaseModel):
    rssi: Optional[float] = None
    messages_count: int = 0
    uptime: str = "0s"

# ===================== GESTIÓN DE ESTADO =====================

class ChatState:
    """Gestiona el estado global del chat"""
    
    def __init__(self):
        self.communicator: Optional[LoRaSerialCommunicator] = None
        self.active_connections: List[WebSocket] = []
        self.messages: List[Message] = []
        self.user_name: str = ""
        self.is_connected: bool = False
        self.current_port: Optional[str] = None
        self.start_time = datetime.now()
        self.rssi: Optional[float] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    async def broadcast(self, message: dict):
        """Envía un mensaje a todos los clientes WebSocket conectados"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
    
    def add_message(self, sender: str, content: str, rssi: Optional[str] = None):
        """Agrega un mensaje al historial"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = Message(sender=sender, content=content, timestamp=timestamp)
        self.messages.append(msg)
        
        # Limitar historial a 100 mensajes
        if len(self.messages) > 100:
            self.messages.pop(0)
        
        # Actualizar RSSI si se proporciona
        if rssi:
            try:
                self.rssi = float(rssi)
            except (ValueError, TypeError) as e:
                logger.debug(f"No se pudo convertir RSSI a float: {rssi}")
                pass
        
        return msg

state = ChatState()

# ===================== CALLBACKS DEL COMUNICADOR =====================

def on_message_received(sender: str, message: str, rssi: str):
    """Callback cuando se recibe un mensaje LoRa"""
    msg = state.add_message(sender, message, rssi)
    
    # Broadcast a todos los clientes web
    if state.loop and state.loop.is_running():
        asyncio.run_coroutine_threadsafe(
            state.broadcast({
                "type": "message",
                "data": {
                    "sender": sender,
                    "content": message,
                    "timestamp": msg.timestamp,
                    "rssi": rssi,
                    "is_own": False
                }
            }),
            state.loop
        )

def on_status_update(status: str):
    """Callback para actualizaciones de estado"""
    if state.loop and state.loop.is_running():
        asyncio.run_coroutine_threadsafe(
            state.broadcast({
                "type": "status",
                "data": status
            }),
            state.loop
        )

def on_error(error: str):
    """Callback para errores"""
    if state.loop and state.loop.is_running():
        asyncio.run_coroutine_threadsafe(
            state.broadcast({
                "type": "error",
                "data": error
            }),
            state.loop
        )

# ===================== ENDPOINTS REST =====================

@app.get("/")
async def read_root():
    """Sirve la página principal"""
    return FileResponse("static/index.html")

@app.get("/api/ports")
async def get_available_ports():
    """Lista todos los puertos serie disponibles (COM, ttyUSB, ttyACM, etc.) con descripción"""
    try:
        ports = LoRaSerialCommunicator.list_available_ports()
        return {"ports": ports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ports/detect")
async def detect_lora_ports():
    """Detecta automáticamente puertos con dispositivos LoRa P2P mediante PING/PONG"""
    try:
        logger.info("🔍 Iniciando detección automática de dispositivos LoRa...")
        lora_ports = LoRaSerialCommunicator.detect_lora_ports()
        all_ports = LoRaSerialCommunicator.list_available_ports()
        
        if lora_ports:
            logger.info(f"✅ Dispositivos LoRa detectados: {', '.join(lora_ports)}")
        else:
            logger.warning("⚠️  No se detectaron dispositivos LoRa")
        
        return {
            "lora_ports": lora_ports,
            "all_ports": all_ports,
            "detected": len(lora_ports) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/connect")
async def connect_device(config: UserConfig):
    """Conecta al dispositivo LoRa"""
    try:
        logger.info(f"🔌 Solicitando conexión a {config.port} para usuario '{config.name}'")
        
        # Desconectar si ya está conectado
        if state.communicator and state.is_connected:
            state.communicator.disconnect()
        
        # Crear nuevo comunicador
        state.communicator = LoRaSerialCommunicator()
        state.communicator.on_message_received = on_message_received
        state.communicator.on_status_update = on_status_update
        state.communicator.on_error = on_error
        
        # Conectar
        if state.communicator.connect(config.port):
            state.is_connected = True
            state.user_name = config.name
            state.current_port = config.port
            state.start_time = datetime.now()
            
            logger.info(f"✅ Conexión exitosa - Usuario: {config.name}, Puerto: {config.port}")
            
            return {
                "success": True,
                "message": "Conectado exitosamente",
                "name": config.name,
                "port": config.port
            }
        else:
            raise HTTPException(status_code=500, detail="No se pudo conectar al dispositivo")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/disconnect")
async def disconnect_device():
    """Desconecta del dispositivo LoRa"""
    try:
        logger.info("🔌 Solicitando desconexión...")
        
        if state.communicator:
            state.communicator.disconnect()
        
        state.is_connected = False
        state.current_port = None
        
        logger.info("✅ Desconectado exitosamente")
        
        return {"success": True, "message": "Desconectado"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send")
async def send_message(message: Message):
    """Envía un mensaje vía LoRa"""
    try:
        if not state.is_connected or not state.communicator:
            logger.warning("⚠️  Intento de envío sin conexión activa")
            raise HTTPException(status_code=400, detail="No conectado al dispositivo")
        
        # Validar longitud del mensaje
        if len(message.content) > 96:
            logger.warning(f"⚠️  Mensaje demasiado largo: {len(message.content)} caracteres")
            raise HTTPException(status_code=400, detail="Mensaje demasiado largo (máx 96 caracteres)")
        
        logger.info(f"📤 API: Solicitando envío de mensaje de '{message.sender}': {message.content}")
        if not state.is_connected or not state.communicator:
            raise HTTPException(status_code=400, detail="No hay conexión con el dispositivo")
        
        if not state.user_name:
            raise HTTPException(status_code=400, detail="Nombre de usuario no configurado")
        
        # Enviar mensaje
        if state.communicator.send_message(state.user_name, message.content):
            # Agregar al historial
            msg = state.add_message(state.user_name, message.content)
            
            # Broadcast a todos los clientes
            await state.broadcast({
                "type": "message",
                "data": {
                    "sender": state.user_name,
                    "content": message.content,
                    "timestamp": msg.timestamp,
                    "is_own": True
                }
            })
            
            return {"success": True, "message": "Mensaje enviado"}
        else:
            raise HTTPException(status_code=500, detail="Error al enviar mensaje")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages")
async def get_messages():
    """Obtiene el historial de mensajes"""
    return {
        "messages": [
            {
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "is_own": msg.sender == state.user_name
            }
            for msg in state.messages
        ]
    }

@app.get("/api/status")
async def get_status():
    """Obtiene el estado del sistema"""
    uptime = datetime.now() - state.start_time
    
    return {
        "connected": state.is_connected,
        "port": state.current_port,
        "user_name": state.user_name,
        "rssi": state.rssi,
        "messages_count": len(state.messages),
        "uptime": str(uptime).split('.')[0]
    }

# ===================== WEBSOCKET =====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicación en tiempo real"""
    await websocket.accept()
    state.active_connections.append(websocket)
    
    try:
        # Enviar estado actual al conectarse
        await websocket.send_json({
            "type": "status",
            "data": {
                "connected": state.is_connected,
                "user_name": state.user_name
            }
        })
        
        # Mantener conexión activa
        while True:
            # Recibir mensajes del cliente (ping/pong para keep-alive)
            data = await websocket.receive_text()
            
            # Echo para keep-alive
            if data == "ping":
                await websocket.send_text("pong")
    
    except WebSocketDisconnect:
        state.active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in state.active_connections:
            state.active_connections.remove(websocket)

# ===================== ARCHIVOS ESTÁTICOS =====================

# Montar directorio de archivos estáticos (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===================== INICIALIZACIÓN =====================

@app.on_event("startup")
async def startup_event():
    """Eventos al iniciar la aplicación"""
    # Guardar el event loop para usarlo en callbacks desde threads
    state.loop = asyncio.get_running_loop()
    
    print("=" * 50)
    print("🚀 LoRa P2P Chat Web Server Starting...")
    print("=" * 50)
    print(f"📡 API disponible en: http://localhost:8000")
    print(f"🌐 Web UI disponible en: http://localhost:8000")
    print(f"📚 Documentación API: http://localhost:8000/docs")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Eventos al cerrar la aplicación"""
    if state.communicator and state.is_connected:
        state.communicator.disconnect()
    print("\n👋 LoRa P2P Chat Web Server Stopped")

# ===================== EJECUCIÓN =====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
