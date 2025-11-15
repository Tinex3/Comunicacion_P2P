"""
Interfaz Gráfica para Sistema de Comunicación LoRa P2P
Aplicación de chat usando tecnología LoRa con ESP32
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import json
import os
from serial_comm import LoRaSerialCommunicator


class LoRaChatGUI:
    """Clase principal de la interfaz gráfica"""
    
    CONFIG_FILE = "lora_chat_config.json"
    
    def __init__(self, root):
        """
        Inicializa la interfaz gráfica
        
        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.root.title("LoRa P2P Chat - Tekroy Desarrollos")
        self.root.geometry("800x600")
        
        # Configuración
        self.config = self.load_config()
        self.user_name = self.config.get("user_name", "")
        self.last_port = self.config.get("last_port", "")
        
        # Comunicador serial
        self.communicator = LoRaSerialCommunicator()
        self.communicator.on_message_received = self.on_message_received
        self.communicator.on_status_update = self.on_status_update
        self.communicator.on_error = self.on_error
        
        # Construir interfaz
        self.build_ui()
        
        # Si hay nombre guardado, mostrar ventana principal
        if self.user_name:
            self.show_chat_window()
        else:
            self.show_setup_window()
    
    def load_config(self):
        """Carga la configuración desde archivo JSON"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error al cargar configuración: {e}")
                return {}
        return {}
    
    def save_config(self):
        """Guarda la configuración en archivo JSON"""
        self.config["user_name"] = self.user_name
        self.config["last_port"] = self.last_port
        
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
    
    def build_ui(self):
        """Construye toda la interfaz de usuario"""
        # Frame de configuración inicial
        self.setup_frame = ttk.Frame(self.root, padding="20")
        
        # Frame principal de chat
        self.chat_frame = ttk.Frame(self.root)
        
        # Construir ambas interfaces
        self.build_setup_ui()
        self.build_chat_ui()
    
    # ==================== INTERFAZ DE CONFIGURACIÓN ====================
    
    def build_setup_ui(self):
        """Construye la interfaz de configuración inicial"""
        # Título
        title_label = ttk.Label(
            self.setup_frame,
            text="Configuración de LoRa Chat",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Nombre de usuario
        name_frame = ttk.Frame(self.setup_frame)
        name_frame.pack(pady=10, fill='x')
        
        ttk.Label(name_frame, text="Tu nombre:", font=("Helvetica", 12)).pack(anchor='w')
        self.name_entry = ttk.Entry(name_frame, font=("Helvetica", 12), width=30)
        self.name_entry.pack(pady=5, fill='x')
        self.name_entry.insert(0, self.user_name)
        
        # Puerto serial
        port_frame = ttk.Frame(self.setup_frame)
        port_frame.pack(pady=10, fill='x')
        
        ttk.Label(port_frame, text="Puerto Serial:", font=("Helvetica", 12)).pack(anchor='w')
        
        port_select_frame = ttk.Frame(port_frame)
        port_select_frame.pack(pady=5, fill='x')
        
        self.port_combo = ttk.Combobox(
            port_select_frame,
            font=("Helvetica", 11),
            state='readonly'
        )
        self.port_combo.pack(side='left', fill='x', expand=True)
        
        refresh_btn = ttk.Button(
            port_select_frame,
            text="🔄 Actualizar",
            command=self.refresh_ports,
            width=15
        )
        refresh_btn.pack(side='left', padx=5)
        
        # Botón detectar automáticamente
        detect_btn = ttk.Button(
            port_select_frame,
            text="🔍 Auto-detectar",
            command=self.auto_detect_ports,
            width=15
        )
        detect_btn.pack(side='left', padx=5)
        
        # Botón conectar
        connect_btn = ttk.Button(
            self.setup_frame,
            text="Conectar y Comenzar",
            command=self.start_chat,
            style="Accent.TButton"
        )
        connect_btn.pack(pady=20)
        
        # Estado de conexión
        self.setup_status_label = ttk.Label(
            self.setup_frame,
            text="",
            font=("Helvetica", 10),
            foreground="gray"
        )
        self.setup_status_label.pack(pady=10)
        
        # Refrescar puertos al inicio
        self.refresh_ports()
    
    def refresh_ports(self):
        """Actualiza la lista de puertos serie disponibles (COM, ttyUSB, ttyACM, etc.)"""
        ports = LoRaSerialCommunicator.list_available_ports()
        self.port_combo['values'] = ports
        
        if ports:
            # Buscar el último puerto usado (comparando solo el nombre del dispositivo)
            last_port_found = False
            if self.last_port:
                # Extraer el nombre del dispositivo del último puerto guardado
                last_port_device = self.last_port.split(' - ')[0]
                for port in ports:
                    if port.startswith(last_port_device):
                        self.port_combo.set(port)
                        last_port_found = True
                        break
            
            # Si no se encuentra el último puerto, seleccionar el primero
            if not last_port_found:
                self.port_combo.current(0)
            
            self.setup_status_label.config(
                text=f"{len(ports)} puerto(s) encontrado(s)",
                foreground="green"
            )
        else:
            self.setup_status_label.config(
                text="No se encontraron puertos serie",
                foreground="red"
            )
    
    def auto_detect_ports(self):
        """Detecta automáticamente puertos con dispositivos LoRa P2P"""
        self.setup_status_label.config(text="Detectando dispositivos LoRa...", foreground="blue")
        self.root.update()
        
        def progress_callback(port, current, total):
            """Actualiza el estado durante la detección"""
            self.setup_status_label.config(
                text=f"Probando {current}/{total}: {port.split(' - ')[0]}...",
                foreground="blue"
            )
            self.root.update()
        
        # Ejecutar detección en thread para no bloquear UI
        import threading
        
        def detect_thread():
            lora_ports = LoRaSerialCommunicator.detect_lora_ports(progress_callback)
            
            # Actualizar UI en thread principal
            self.root.after(0, lambda: self.on_detection_complete(lora_ports))
        
        thread = threading.Thread(target=detect_thread, daemon=True)
        thread.start()
    
    def on_detection_complete(self, lora_ports):
        """Callback cuando la detección automática termina"""
        if lora_ports:
            self.port_combo['values'] = lora_ports
            self.port_combo.current(0)
            self.setup_status_label.config(
                text=f"✅ {len(lora_ports)} dispositivo(s) LoRa encontrado(s)",
                foreground="green"
            )
        else:
            all_ports = LoRaSerialCommunicator.list_available_ports()
            self.port_combo['values'] = all_ports
            if all_ports:
                self.port_combo.current(0)
            self.setup_status_label.config(
                text="⚠️ No se detectaron dispositivos LoRa (mostrando todos los puertos)",
                foreground="orange"
            )
    
    def start_chat(self):
        """Inicia la conexión y muestra la ventana de chat"""
        # Validar nombre
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Por favor ingresa tu nombre")
            return
        
        if len(name) > 30:
            messagebox.showerror("Error", "El nombre es demasiado largo (máx 30 caracteres)")
            return
        
        # Validar puerto
        port = self.port_combo.get()
        if not port:
            messagebox.showerror("Error", "Por favor selecciona un puerto serie")
            return
        
        # Guardar configuración
        self.user_name = name
        self.last_port = port
        self.save_config()
        
        # Conectar
        self.setup_status_label.config(text="Conectando...", foreground="blue")
        self.root.update()
        
        if self.communicator.connect(port):
            self.show_chat_window()
        else:
            messagebox.showerror(
                "Error de Conexión",
                f"No se pudo conectar al puerto {port}\n\n"
                "Verifica que:\n"
                "- El dispositivo esté conectado\n"
                "- El puerto sea correcto\n"
                "- No esté siendo usado por otra aplicación"
            )
            self.setup_status_label.config(text="Error de conexión", foreground="red")
    
    # ==================== INTERFAZ DE CHAT ====================
    
    def build_chat_ui(self):
        """Construye la interfaz principal de chat"""
        # Barra superior
        top_bar = ttk.Frame(self.chat_frame, padding="10")
        top_bar.pack(fill='x', side='top')
        
        # Título con nombre de usuario
        self.title_label = ttk.Label(
            top_bar,
            text=f"LoRa Chat - {self.user_name}",
            font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(side='left')
        
        # Estado de conexión
        self.connection_label = ttk.Label(
            top_bar,
            text="● Conectado",
            font=("Helvetica", 10),
            foreground="green"
        )
        self.connection_label.pack(side='right', padx=10)
        
        # Botón configuración
        config_btn = ttk.Button(
            top_bar,
            text="⚙ Configuración",
            command=self.show_setup_window,
            width=15
        )
        config_btn.pack(side='right')
        
        # Área de mensajes
        messages_frame = ttk.Frame(self.chat_frame, padding="10")
        messages_frame.pack(fill='both', expand=True)
        
        ttk.Label(
            messages_frame,
            text="Mensajes:",
            font=("Helvetica", 11, "bold")
        ).pack(anchor='w')
        
        # ScrolledText para mensajes
        self.messages_text = scrolledtext.ScrolledText(
            messages_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            state='disabled',
            bg="#f5f5f5"
        )
        self.messages_text.pack(fill='both', expand=True, pady=5)
        
        # Configurar tags para colores
        self.messages_text.tag_config("own", foreground="#0066cc", font=("Consolas", 10, "bold"))
        self.messages_text.tag_config("other", foreground="#cc6600", font=("Consolas", 10, "bold"))
        self.messages_text.tag_config("system", foreground="#666666", font=("Consolas", 9, "italic"))
        self.messages_text.tag_config("time", foreground="#999999", font=("Consolas", 8))
        
        # Área de entrada
        input_frame = ttk.Frame(self.chat_frame, padding="10")
        input_frame.pack(fill='x', side='bottom')
        
        ttk.Label(
            input_frame,
            text="Tu mensaje:",
            font=("Helvetica", 11)
        ).pack(anchor='w')
        
        # Frame para entrada y botón
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill='x', pady=5)
        
        self.message_entry = ttk.Entry(
            entry_frame,
            font=("Helvetica", 11)
        )
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        self.send_button = ttk.Button(
            entry_frame,
            text="📤 Enviar",
            command=self.send_message,
            width=12
        )
        self.send_button.pack(side='left')
        
        # Contador de caracteres
        self.char_count_label = ttk.Label(
            input_frame,
            text="0/96",
            font=("Helvetica", 9),
            foreground="gray"
        )
        self.char_count_label.pack(anchor='e')
        
        self.message_entry.bind('<KeyRelease>', self.update_char_count)
        
        # Barra de estado inferior
        status_bar = ttk.Frame(self.chat_frame)
        status_bar.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(
            status_bar,
            text="Listo",
            font=("Helvetica", 9),
            foreground="gray",
            padding="5"
        )
        self.status_label.pack(side='left')
        
        self.rssi_label = ttk.Label(
            status_bar,
            text="RSSI: --",
            font=("Helvetica", 9),
            foreground="gray",
            padding="5"
        )
        self.rssi_label.pack(side='right')
    
    # ==================== FUNCIONES DE NAVEGACIÓN ====================
    
    def show_setup_window(self):
        """Muestra la ventana de configuración"""
        self.chat_frame.pack_forget()
        self.setup_frame.pack(fill='both', expand=True)
        self.name_entry.focus()
    
    def show_chat_window(self):
        """Muestra la ventana de chat"""
        self.setup_frame.pack_forget()
        self.chat_frame.pack(fill='both', expand=True)
        self.title_label.config(text=f"LoRa Chat - {self.user_name}")
        self.message_entry.focus()
        
        # Mensaje de bienvenida
        self.add_system_message("Sistema iniciado. ¡Listo para chatear!")
    
    # ==================== FUNCIONES DE MENSAJERÍA ====================
    
    def send_message(self):
        """Envía un mensaje vía LoRa"""
        message = self.message_entry.get().strip()
        
        if not message:
            return
        
        if len(message) > 96:
            messagebox.showwarning(
                "Mensaje muy largo",
                "El mensaje no puede exceder 96 caracteres"
            )
            return
        
        # Enviar vía LoRa
        if self.communicator.send_message(self.user_name, message):
            # Mostrar mensaje propio
            self.add_own_message(message)
            self.message_entry.delete(0, tk.END)
            self.update_char_count()
        else:
            messagebox.showerror("Error", "No se pudo enviar el mensaje")
    
    def add_own_message(self, message: str):
        """Agrega un mensaje propio al área de chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, f"[{timestamp}] ", "time")
        self.messages_text.insert(tk.END, f"{self.user_name}: ", "own")
        self.messages_text.insert(tk.END, f"{message}\n")
        self.messages_text.see(tk.END)
        self.messages_text.config(state='disabled')
    
    def add_received_message(self, sender: str, message: str, rssi: str = ""):
        """Agrega un mensaje recibido al área de chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, f"[{timestamp}] ", "time")
        self.messages_text.insert(tk.END, f"{sender}: ", "other")
        self.messages_text.insert(tk.END, f"{message}\n")
        self.messages_text.see(tk.END)
        self.messages_text.config(state='disabled')
        
        # Actualizar RSSI
        if rssi:
            self.rssi_label.config(text=f"RSSI: {rssi} dBm")
    
    def add_system_message(self, message: str):
        """Agrega un mensaje del sistema"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.messages_text.config(state='normal')
        self.messages_text.insert(tk.END, f"[{timestamp}] ", "time")
        self.messages_text.insert(tk.END, f"[SISTEMA] {message}\n", "system")
        self.messages_text.see(tk.END)
        self.messages_text.config(state='disabled')
    
    def update_char_count(self, event=None):
        """Actualiza el contador de caracteres"""
        count = len(self.message_entry.get())
        self.char_count_label.config(text=f"{count}/96")
        
        if count > 96:
            self.char_count_label.config(foreground="red")
        else:
            self.char_count_label.config(foreground="gray")
    
    # ==================== CALLBACKS DEL COMUNICADOR ====================
    
    def on_message_received(self, sender: str, message: str, rssi: str):
        """Callback cuando se recibe un mensaje"""
        # Ejecutar en el thread principal de Tkinter
        self.root.after(0, lambda: self.add_received_message(sender, message, rssi))
    
    def on_status_update(self, status: str):
        """Callback para actualizaciones de estado"""
        self.root.after(0, lambda: self.status_label.config(text=status))
    
    def on_error(self, error: str):
        """Callback para errores"""
        self.root.after(0, lambda: self.add_system_message(f"ERROR: {error}"))
    
    # ==================== CIERRE DE APLICACIÓN ====================
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            self.communicator.disconnect()
            self.save_config()
            self.root.destroy()


def main():
    """Función principal"""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Crear aplicación
    app = LoRaChatGUI(root)
    
    # Configurar cierre
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Iniciar loop
    root.mainloop()


if __name__ == "__main__":
    main()
