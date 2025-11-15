// ===================== CONFIGURACIÓN =====================

const API_URL = window.location.origin;
const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

let ws = null;
let userName = '';
let isConnected = false;

// ===================== INICIALIZACIÓN =====================

document.addEventListener('DOMContentLoaded', () => {
    // Cargar puertos al inicio
    refreshPorts();
    
    // Event listeners
    document.getElementById('messageInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    document.getElementById('messageInput').addEventListener('input', updateCharCounter);
    
    // Conectar WebSocket
    connectWebSocket();
});

// ===================== WEBSOCKET =====================

function connectWebSocket() {
    ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        setInterval(() => ws.send('ping'), 30000); // Keep-alive cada 30s
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
        console.log('❌ WebSocket desconectado');
        // Reconectar después de 3 segundos
        setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'message':
            addMessageToUI(data.data);
            break;
        case 'status':
            if (typeof data.data === 'object') {
                updateConnectionStatus(data.data);
            } else {
                showStatus(data.data);
            }
            break;
        case 'error':
            showAlert(data.data, 'error');
            break;
    }
}

// ===================== API CALLS =====================

async function refreshPorts() {
    try {
        const response = await fetch(`${API_URL}/api/ports`);
        const data = await response.json();
        
        const portSelect = document.getElementById('portSelect');
        portSelect.innerHTML = '';
        
        if (data.ports && data.ports.length > 0) {
            data.ports.forEach(port => {
                const option = document.createElement('option');
                option.value = port;
                option.textContent = port;
                portSelect.appendChild(option);
            });
            showAlert(`${data.ports.length} puerto(s) encontrado(s)`, 'success');
        } else {
            portSelect.innerHTML = '<option value="">No se encontraron puertos</option>';
            showAlert('No se encontraron puertos serie', 'error');
        }
    } catch (error) {
        console.error('Error cargando puertos:', error);
        showAlert('Error al cargar puertos', 'error');
    }
}

async function autoDetectPorts() {
    try {
        showAlert('🔍 Detectando dispositivos LoRa P2P...', 'info');
        
        const response = await fetch(`${API_URL}/api/ports/detect`);
        const data = await response.json();
        
        const portSelect = document.getElementById('portSelect');
        portSelect.innerHTML = '';
        
        if (data.lora_ports && data.lora_ports.length > 0) {
            // Mostrar solo puertos LoRa detectados
            data.lora_ports.forEach(port => {
                const option = document.createElement('option');
                option.value = port;
                option.textContent = `✅ ${port}`;
                portSelect.appendChild(option);
            });
            showAlert(`✅ ${data.lora_ports.length} dispositivo(s) LoRa encontrado(s)`, 'success');
        } else {
            // No se detectaron dispositivos LoRa, mostrar todos los puertos
            if (data.all_ports && data.all_ports.length > 0) {
                data.all_ports.forEach(port => {
                    const option = document.createElement('option');
                    option.value = port;
                    option.textContent = port;
                    portSelect.appendChild(option);
                });
                showAlert('⚠️ No se detectaron dispositivos LoRa (mostrando todos los puertos)', 'warning');
            } else {
                portSelect.innerHTML = '<option value="">No se encontraron puertos</option>';
                showAlert('No se encontraron puertos serie', 'error');
            }
        }
    } catch (error) {
        console.error('Error en auto-detección:', error);
        showAlert('Error en auto-detección. Intenta refrescar manualmente.', 'error');
    }
}


async function connect() {
    const name = document.getElementById('nameInput').value.trim();
    const port = document.getElementById('portSelect').value;
    
    if (!name) {
        showAlert('Por favor ingresa tu nombre', 'error');
        return;
    }
    
    if (!port) {
        showAlert('Por favor selecciona un puerto', 'error');
        return;
    }
    
    try {
        const connectBtn = document.getElementById('connectBtn');
        connectBtn.disabled = true;
        connectBtn.textContent = 'Conectando...';
        
        const response = await fetch(`${API_URL}/api/connect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, port })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            userName = name;
            isConnected = true;
            
            // Cambiar a pantalla de chat
            document.getElementById('setupScreen').style.display = 'none';
            document.getElementById('chatScreen').classList.add('active');
            document.getElementById('userName').textContent = userName;
            document.getElementById('statusIndicator').classList.add('connected');
            
            // Agregar mensaje de sistema
            addSystemMessage('Sistema conectado. ¡Listo para chatear!');
            
            // Cargar mensajes previos
            loadMessages();
            
            // Focus en input
            document.getElementById('messageInput').focus();
        } else {
            throw new Error(data.detail || 'Error al conectar');
        }
    } catch (error) {
        console.error('Error conectando:', error);
        showAlert(error.message, 'error');
    } finally {
        const connectBtn = document.getElementById('connectBtn');
        connectBtn.disabled = false;
        connectBtn.textContent = 'Conectar';
    }
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    if (message.length > 96) {
        showAlert('El mensaje es demasiado largo (máx 96 caracteres)', 'error');
        return;
    }
    
    try {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = true;
        
        const response = await fetch(`${API_URL}/api/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sender: userName, content: message })
        });
        
        if (response.ok) {
            input.value = '';
            updateCharCounter();
        } else {
            const data = await response.json();
            showAlert(data.detail || 'Error al enviar mensaje', 'error');
        }
    } catch (error) {
        console.error('Error enviando mensaje:', error);
        showAlert('Error al enviar mensaje', 'error');
    } finally {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = false;
        document.getElementById('messageInput').focus();
    }
}

async function loadMessages() {
    try {
        const response = await fetch(`${API_URL}/api/messages`);
        const data = await response.json();
        
        data.messages.forEach(msg => {
            addMessageToUI({
                sender: msg.sender,
                content: msg.content,
                timestamp: msg.timestamp,
                is_own: msg.is_own
            }, false);
        });
        
        scrollToBottom();
    } catch (error) {
        console.error('Error cargando mensajes:', error);
    }
}

async function getStatus() {
    try {
        const response = await fetch(`${API_URL}/api/status`);
        const data = await response.json();
        
        updateStatus(data);
    } catch (error) {
        console.error('Error obteniendo estado:', error);
    }
}

// ===================== UI FUNCTIONS =====================

function addMessageToUI(data, scroll = true) {
    const messagesArea = document.getElementById('messagesArea');
    const messageDiv = document.createElement('div');
    
    if (data.is_own) {
        messageDiv.className = 'message own';
        messageDiv.innerHTML = `
            <div class="message-time">${data.timestamp || ''}</div>
            <div class="message-content">
                <div class="message-sender">${data.sender}</div>
                ${escapeHtml(data.content)}
            </div>
        `;
    } else {
        messageDiv.className = 'message other';
        messageDiv.innerHTML = `
            <div class="message-time">${data.timestamp || ''}</div>
            <div class="message-content">
                <div class="message-sender">${data.sender}</div>
                ${escapeHtml(data.content)}
            </div>
        `;
    }
    
    messagesArea.appendChild(messageDiv);
    
    if (scroll) {
        scrollToBottom();
    }
    
    // Actualizar RSSI si está disponible
    if (data.rssi) {
        document.getElementById('rssiValue').textContent = `${data.rssi} dBm`;
    }
}

function addSystemMessage(message) {
    const messagesArea = document.getElementById('messagesArea');
    const messageDiv = document.createElement('div');
    
    const now = new Date();
    const timestamp = now.toTimeString().split(' ')[0].substring(0, 8);
    
    messageDiv.className = 'message system';
    messageDiv.innerHTML = `
        <div class="message-time">${timestamp}</div>
        <div class="message-content">
            [SISTEMA] ${escapeHtml(message)}
        </div>
    `;
    
    messagesArea.appendChild(messageDiv);
    scrollToBottom();
}

function showAlert(message, type = 'error') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    // Auto-hide después de 5 segundos
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function showStatus(message) {
    document.getElementById('statusText').textContent = message;
}

function updateConnectionStatus(status) {
    if (status.connected) {
        isConnected = true;
        document.getElementById('statusIndicator').classList.add('connected');
    } else {
        isConnected = false;
        document.getElementById('statusIndicator').classList.remove('connected');
    }
}

function updateStatus(data) {
    if (data.rssi !== null && data.rssi !== undefined) {
        document.getElementById('rssiValue').textContent = `${data.rssi} dBm`;
    }
}

function updateCharCounter() {
    const input = document.getElementById('messageInput');
    const counter = document.getElementById('charCounter');
    const count = input.value.length;
    
    counter.textContent = `${count}/96`;
    
    if (count > 96) {
        counter.style.color = 'var(--danger-color)';
    } else {
        counter.style.color = 'var(--text-secondary)';
    }
}

function scrollToBottom() {
    const messagesArea = document.getElementById('messagesArea');
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===================== POLLING DE ESTADO =====================

// Actualizar estado cada 5 segundos
setInterval(() => {
    if (isConnected) {
        getStatus();
    }
}, 5000);
