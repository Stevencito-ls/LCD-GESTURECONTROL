import tkinter as tk
from PIL import Image, ImageTk
import cv2
import win32gui
import win32con

class GestureOverlay:
    def __init__(self):
        self.root = tk.Tk()
        
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        
        # Ajuste de Chroma Key para evitar colisiones con sombras
        self.transparent_color = '#010203' 
        self.root.wm_attributes("-transparentcolor", self.transparent_color)
        self.root.config(bg=self.transparent_color)
        
        # MODO PRODUCCIÓN: Si deseas que el mouse atraviese la cámara,
        # quita los '#' de las siguientes 4 líneas de código:
        
        # hwnd = int(self.root.frame(), 16)
        # styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        # styles = styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        # win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        
        # Posicionar la cámara en la esquina superior izquierda de forma segura
        self.cam_label = tk.Label(self.root, bg=self.transparent_color)
        self.cam_label.place(x=50, y=50) 

    def update_camera_feed(self, frame):
        preview = cv2.resize(frame, (320, 240))
        rgb_image = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        tk_image = ImageTk.PhotoImage(image=pil_image)
        
        self.cam_label.imgtk = tk_image 
        self.cam_label.configure(image=tk_image)

    def update(self):
        self.root.update()