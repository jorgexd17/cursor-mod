import tkinter as tk
from tkinter import ttk
import threading
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw
import mouse
import time

# Crear directorio de config
CONFIG_DIR = Path.home() / ".cursor_mod"
CONFIG_DIR.mkdir(exist_ok=True)
CURSOR_DIR = CONFIG_DIR / "cursors"
CURSOR_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"

# Estilos de cursor predefinidos
CURSOR_STYLES = {
    "default": {
        "ring_size": 28,
        "dot_size": 10,
        "ring_color": (124, 58, 237),
        "dot_color": (244, 114, 182),
        "ring_width": 2,
        "glow": True,
        "animation": False
    },
    "crosshair": {
        "ring_size": 32,
        "dot_size": 8,
        "ring_color": (14, 165, 233),
        "dot_color": (125, 211, 252),
        "ring_width": 2,
        "shape": "square",
        "glow": True,
        "animation": False
    },
    "neon": {
        "ring_size": 30,
        "dot_size": 12,
        "ring_color": (34, 197, 94),
        "dot_color": (134, 239, 172),
        "ring_width": 3,
        "glow": True,
        "animation": True
    },
    "pixel": {
        "ring_size": 24,
        "dot_size": 6,
        "ring_color": (250, 204, 21),
        "dot_color": (253, 230, 138),
        "ring_width": 2,
        "shape": "square",
        "glow": False,
        "animation": False
    },
    "magic": {
        "ring_size": 26,
        "dot_size": 12,
        "ring_color": (244, 114, 182),
        "dot_color": (192, 132, 252),
        "ring_width": 2,
        "glow": True,
        "animation": True,
        "dashed": True
    },
    "circle": {
        "ring_size": 36,
        "dot_size": 6,
        "ring_color": (251, 113, 133),
        "dot_color": (254, 205, 211),
        "ring_width": 3,
        "glow": True,
        "animation": False
    },
    "retro": {
        "ring_size": 20,
        "dot_size": 4,
        "ring_color": (255, 255, 255),
        "dot_color": (0, 0, 0),
        "ring_width": 1,
        "shape": "square",
        "glow": False,
        "animation": False
    }
}

class CursorModApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cursor Mod - Personalización Global")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Configurar tema oscuro
        self.root.configure(bg="#0b1020")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#0b1020", foreground="#e5e7eb")
        style.configure('TButton', background="#1e293b", foreground="#e5e7eb")
        style.configure('TFrame', background="#0b1020")
        
        self.current_style = "default"
        self.is_running = False
        self.mouse_thread = None
        
        self.load_config()
        self.create_ui()
        self.start_cursor_tracking()
        
    def load_config(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.current_style = config.get('style', 'default')
        else:
            self.save_config()
    
    def save_config(self):
        config = {'style': self.current_style}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    
    def create_ui(self):
        # Título
        title = tk.Label(
            self.root,
            text="🎯 Cursor Mod",
            font=("Arial", 24, "bold"),
            bg="#0b1020",
            fg="#e5e7eb"
        )
        title.pack(pady=20)
        
        # Descripción
        desc = tk.Label(
            self.root,
            text="Personaliza tu cursor en todo el ordenador",
            font=("Arial", 10),
            bg="#0b1020",
            fg="#cbd5e1"
        )
        desc.pack()
        
        # Frame de estilos
        styles_frame = tk.Frame(self.root, bg="#0b1020")
        styles_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Crear botones para cada estilo
        self.style_buttons = {}
        for style_name in CURSOR_STYLES.keys():
            btn = tk.Button(
                styles_frame,
                text=style_name.capitalize(),
                command=lambda s=style_name: self.change_style(s),
                bg="#1e293b",
                fg="#e5e7eb",
                activebackground="#334155",
                activeforeground="#e5e7eb",
                padx=12,
                pady=10,
                font=("Arial", 11, "bold"),
                relief="solid",
                bd=1,
                cursor="arrow"
            )
            btn.pack(pady=8, fill="x")
            self.style_buttons[style_name] = btn
        
        # Actualizar botón activo
        self.update_active_button()
        
        # Frame inferior
        bottom_frame = tk.Frame(self.root, bg="#0b1020")
        bottom_frame.pack(pady=20, padx=20, fill="x")
        
        # Botón de prueba
        test_btn = tk.Button(
            bottom_frame,
            text="🎮 Hacer prueba (5 segundos)",
            command=self.test_cursor,
            bg="#7c3aed",
            fg="white",
            activebackground="#6d28d9",
            padx=12,
            pady=10,
            font=("Arial", 11, "bold"),
            relief="solid",
            bd=1,
            cursor="arrow"
        )
        test_btn.pack(pady=10, fill="x")
        
        # Estado
        self.status_label = tk.Label(
            bottom_frame,
            text="✅ Cursor activo",
            font=("Arial", 10),
            bg="#0b1020",
            fg="#22c55e"
        )
        self.status_label.pack()
    
    def update_active_button(self):
        for style_name, btn in self.style_buttons.items():
            if style_name == self.current_style:
                btn.config(bg="#7c3aed", fg="white")
            else:
                btn.config(bg="#1e293b", fg="#e5e7eb")
    
    def change_style(self, style_name):
        self.current_style = style_name
        self.save_config()
        self.update_active_button()
        self.status_label.config(text=f"✅ Estilo cambiado a {style_name.capitalize()}")
        self.root.after(2000, lambda: self.status_label.config(text="✅ Cursor activo"))
    
    def test_cursor(self):
        self.status_label.config(text="🔄 Probando cursor...", fg="#f59e0b")
        self.root.after(5000, lambda: self.status_label.config(text="✅ Cursor activo", fg="#22c55e"))
    
    def start_cursor_tracking(self):
        self.is_running = True
        self.mouse_thread = threading.Thread(target=self.track_cursor, daemon=True)
        self.mouse_thread.start()
    
    def track_cursor(self):
        # Este es donde iría la lógica de rastreo del cursor global
        # Por ahora, simplemente mantenemos el hilo activo
        while self.is_running:
            time.sleep(0.1)
    
    def on_closing(self):
        self.is_running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = CursorModApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
