import ctypes
import json
import os
import sys
import threading
import time
from pathlib import Path

import tkinter as tk


WINDOWS = sys.platform.startswith("win")
CONFIG_DIR = Path.home() / "AppData" / "Roaming" / "cursor_mod"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"

STYLES = {
    "default": {
        "size": 26,
        "dot_size": 8,
        "ring_color": "#7c3aed",
        "dot_color": "#f472b6",
        "bg_color": "white",
        "glow": True,
        "shape": "circle",
    },
    "crosshair": {
        "size": 28,
        "dot_size": 6,
        "ring_color": "#38bdf8",
        "dot_color": "#7dd3fc",
        "bg_color": "white",
        "glow": True,
        "shape": "crosshair",
    },
    "neon": {
        "size": 30,
        "dot_size": 12,
        "ring_color": "#22c55e",
        "dot_color": "#86efac",
        "bg_color": "white",
        "glow": True,
        "shape": "circle",
    },
    "pixel": {
        "size": 28,
        "dot_size": 6,
        "ring_color": "#facc15",
        "dot_color": "#fde68a",
        "bg_color": "white",
        "glow": False,
        "shape": "square",
    },
    "magic": {
        "size": 30,
        "dot_size": 10,
        "ring_color": "#f472b6",
        "dot_color": "#c084fc",
        "bg_color": "white",
        "glow": True,
        "shape": "circle",
    },
    "circle": {
        "size": 38,
        "dot_size": 6,
        "ring_color": "#fb7185",
        "dot_color": "#fecdd3",
        "bg_color": "white",
        "glow": True,
        "shape": "circle",
    },
}


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            style = data.get("style", "default")
            if style in STYLES:
                return style
        except Exception:
            pass
    return "default"


def save_config(style_name: str):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"style": style_name}, f, ensure_ascii=False, indent=2)


class CursorApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.style_name = load_config()
        self.clicking = False
        self.x = 0
        self.y = 0
        self.cursor_window = tk.Toplevel(self.root)
        self.cursor_window.attributes("-topmost", True)
        self.cursor_window.attributes("-fullscreen", True)
        self.cursor_window.attributes("-transparentcolor", "white")
        self.cursor_window.overrideredirect(True)
        self.cursor_window.wm_attributes("-alpha", 1.0)
        self.cursor_window.configure(bg="white")

        self.canvas = tk.Canvas(
            self.cursor_window,
            width=self.root.winfo_screenwidth(),
            height=self.root.winfo_screenheight(),
            bg="white",
            highlightthickness=0,
            cursor="none",
        )
        self.canvas.pack(fill="both", expand=True)

        self.cursor_item = None
        self.dot_item = None
        self.bind_events()
        self.apply_style(self.style_name)
        self.position_cursor(0, 0)

    def bind_events(self):
        self.canvas.bind("<Motion>", self.on_move)
        self.canvas.bind("<ButtonPress-1>", lambda e: self.set_clicking(True))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.set_clicking(False))
        self.root.bind("<KeyPress>", self.on_keypress)

    def on_keypress(self, event):
        key = event.keysym.lower()
        if key == "escape":
            self.close()
            return
        if key in {"1", "2", "3", "4", "5", "6"}:
            names = list(STYLES.keys())
            idx = int(key) - 1
            if 0 <= idx < len(names):
                self.apply_style(names[idx])

    def on_move(self, event):
        self.position_cursor(event.x, event.y)

    def set_clicking(self, value):
        self.clicking = value
        self.redraw()

    def position_cursor(self, x, y):
        self.x = x
        self.y = y
        self.redraw()

    def redraw(self):
        style = STYLES[self.style_name]
        size = style["size"]
        dot_size = style["dot_size"]
        ring_color = style["ring_color"]
        dot_color = style["dot_color"]
        glow = style["glow"]
        shape = style["shape"]

        if self.cursor_item is not None:
            self.canvas.delete(self.cursor_item)
        if self.dot_item is not None:
            self.canvas.delete(self.dot_item)

        if shape == "square":
            self.cursor_item = self.canvas.create_rectangle(
                self.x - size / 2,
                self.y - size / 2,
                self.x + size / 2,
                self.y + size / 2,
                width=2,
                outline=ring_color,
                fill="",
                stipple="gray50" if glow else "",
            )
        elif shape == "crosshair":
            self.cursor_item = self.canvas.create_line(
                self.x - size, self.y, self.x + size, self.y,
                fill=ring_color, width=2
            )
            self.canvas.create_line(
                self.x, self.y - size, self.x, self.y + size,
                fill=ring_color, width=2
            )
        else:
            self.cursor_item = self.canvas.create_oval(
                self.x - size / 2,
                self.y - size / 2,
                self.x + size / 2,
                self.y + size / 2,
                width=2,
                outline=ring_color,
                fill="",
                stipple="gray50" if glow else "",
            )

        if self.clicking:
            dot_size = max(4, dot_size - 2)

        self.dot_item = self.canvas.create_oval(
            self.x - dot_size / 2,
            self.y - dot_size / 2,
            self.x + dot_size / 2,
            self.y + dot_size / 2,
            fill=dot_color,
            outline="",
        )

    def apply_style(self, style_name: str):
        self.style_name = style_name
        save_config(style_name)
        self.redraw()

    def close(self):
        if WINDOWS:
            ctypes.windll.user32.ShowCursor(True)
        self.root.destroy()


def hide_system_cursor():
    if WINDOWS:
        ctypes.windll.user32.ShowCursor(False)


def main():
    if not WINDOWS:
        print("Esta versión está diseñada para Windows.")
        return

    root = tk.Tk()
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.0)
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.overrideredirect(True)
    root.config(cursor="none")
    root.focus_set()
    hide_system_cursor()

    app = CursorApp(root)
    try:
        root.mainloop()
    finally:
        app.close()


if __name__ == "__main__":
    main()
