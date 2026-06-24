import pyautogui
import time

class MouseController:
    def __init__(self, smoothing=0.7):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # Soporte Multi-monitor: obtiene el ancho/alto de TODO el escritorio
        self.screen_w, self.screen_h = pyautogui.size()

        self.prev_x, self.prev_y = 0, 0
        self.prev_z = 0  # Para medir el cambio de profundidad
        self.smoothing = smoothing
        
        # Estados
        self.is_clicking = False 
        self.double_click_pressed = False
        self.right_click_pressed = False
        self.middle_click_pressed = False
        self.is_rotating = False
        self.prev_angle = 0
        self.is_panning = False
        self.prev_scroll_x, self.prev_scroll_y = 0, 0
        self.last_swipe_time = 0

    def move_cursor(self, cam_x, cam_y, cam_w, cam_h):
        # Mapeo escalado a la resolución total (abarca todas tus pantallas)
        target_x = int((cam_x / cam_w) * self.screen_w)
        target_y = int((cam_y / cam_h) * self.screen_h)

        smoothed_x = self.prev_x + (target_x - self.prev_x) * self.smoothing
        smoothed_y = self.prev_y + (target_y - self.prev_y) * self.smoothing

        pyautogui.moveTo(smoothed_x, smoothed_y)
        self.prev_x, self.prev_y = smoothed_x, smoothed_y

    def zoom_z_axis(self, current_z):
        # Lógica de Zoom por Profundidad
        if self.prev_z == 0:
            self.prev_z = current_z
            return

        # Umbral para evitar clicks fantasma por vibración
        if abs(current_z - self.prev_z) > 0.05:
            if current_z < self.prev_z:
                pyautogui.hotkey('ctrl', '+') # Mano se acerca
            else:
                pyautogui.hotkey('ctrl', '-') # Mano se aleja
            self.prev_z = current_z

    def drag_and_drop(self, is_pinching):
        if is_pinching and not self.is_clicking:
            pyautogui.mouseDown()
            self.is_clicking = True
        elif not is_pinching and self.is_clicking:
            pyautogui.mouseUp()
            self.is_clicking = False

    def double_click(self, is_pinching_middle):
        if is_pinching_middle and not self.double_click_pressed:
            pyautogui.doubleClick()
            self.double_click_pressed = True
        elif not is_pinching_middle and self.double_click_pressed:
            self.double_click_pressed = False

    def right_click(self, is_pinching_pinky):
        if is_pinching_pinky and not self.right_click_pressed:
            pyautogui.rightClick()
            self.right_click_pressed = True
        elif not is_pinching_pinky and self.right_click_pressed:
            self.right_click_pressed = False

    def middle_click(self, is_pinching_three):
        if is_pinching_three and not self.middle_click_pressed:
            pyautogui.click(button='middle')
            self.middle_click_pressed = True
        elif not is_pinching_three and self.middle_click_pressed:
            self.middle_click_pressed = False

    def trackpad_navigation(self, current_x, current_y, fingers_together):
        current_time = time.time()
        if self.prev_scroll_x == 0: 
            self.prev_scroll_x, self.prev_scroll_y = current_x, current_y
        
        delta_x = current_x - self.prev_scroll_x
        delta_y = current_y - self.prev_scroll_y
        
        if fingers_together:
            if abs(delta_x) > 40 and (current_time - self.last_swipe_time > 1.0):
                if delta_x > 0:
                    pyautogui.hotkey('alt', 'right')
                else:
                    pyautogui.hotkey('alt', 'left')
                self.last_swipe_time = current_time
        elif abs(delta_y) > 5:
            pyautogui.scroll(int(-delta_y * 3))
            
        self.prev_scroll_x, self.prev_scroll_y = current_x, current_y

    def rotate_3d(self, is_pinching_both, current_angle=0):
        if is_pinching_both:
            if not self.is_rotating: 
                pyautogui.mouseDown(button='left') 
                self.is_rotating = True
                self.prev_angle = current_angle
            else:
                delta_angle = current_angle - self.prev_angle
                if abs(delta_angle) > 2: 
                    pyautogui.moveRel(int(delta_angle * 5), 0)
                    self.prev_angle = current_angle
        else:
            if self.is_rotating:
                pyautogui.mouseUp(button='left') 
                self.is_rotating = False
                self.prev_angle = 0

    def pan_3d(self, is_pinching_ring):
        if is_pinching_ring and not self.is_panning: 
            pyautogui.keyDown('shift')           
            pyautogui.mouseDown(button='middle') 
            self.is_panning = True
        elif not is_pinching_ring and self.is_panning: 
            pyautogui.mouseUp(button='middle')   
            pyautogui.keyUp('shift')             
            self.is_panning = False
            
    def reset_all(self):
        self.prev_scroll_x = 0
        self.prev_scroll_y = 0
        self.prev_z = 0