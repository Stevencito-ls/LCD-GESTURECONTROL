import cv2
from gesture_engine import GestureEngine
from mouse_controller import MouseController
from overlay import GestureOverlay

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara web.")
        return

    engine = GestureEngine(max_num_hands=2)
    mouse = MouseController(smoothing=0.7) 
    overlay = GestureOverlay()

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            frame = cv2.flip(frame, 1)
            cam_h, cam_w, _ = frame.shape

            frame, all_hands = engine.process_frame(frame)
            
            # --- MODO 3D: DOS MANOS DETECTADAS ---
            if len(all_hands) == 2:
                hand1, hand2 = all_hands[0], all_hands[1]
                
                dist_h1, info_h1 = engine.get_distance(4, 8, hand1)
                dist_h2, info_h2 = engine.get_distance(4, 8, hand2)
                
                is_pinching_both = dist_h1 < 45 and dist_h2 < 45
                
                if is_pinching_both:
                    current_angle = engine.get_angle(info_h1[4], info_h1[5], info_h2[4], info_h2[5])
                    mouse.rotate_3d(True, current_angle)
                else:
                    mouse.rotate_3d(False)

            # --- MODO 1 MANO: NAVEGACIÓN Y WEB ---
            elif len(all_hands) == 1:
                h = all_hands[0]
                mouse.rotate_3d(False)

                # Gestos y distancias
                dist_left, i_left = engine.get_distance(4, 8, h)
                dist_mid, i_mid = engine.get_distance(4, 12, h)
                dist_ring, i_ring = engine.get_distance(4, 16, h)
                dist_pinky, i_pinky = engine.get_distance(4, 20, h)

                # La muñeca (landmark 0) tiene el valor Z más estable
                z_depth = h[0][3]

                # --- ACTIVACIÓN DE ZOOM Z (Pulgar + Meñique) ---
                is_z_zoom = dist_pinky < 45 and dist_left > 45

                if is_z_zoom:
                    mouse.zoom_z_axis(z_depth)
                else:
                    mouse.prev_z = 0 # Reiniciamos el ancla Z al soltar la pinza

                    # MODO NORMAL: Mover cursor y clicks
                    is_mid_click = (dist_left < 45 and dist_mid < 45)
                    mouse.drag_and_drop(dist_left < 45 and not is_mid_click)
                    mouse.double_click(dist_mid < 45 and not is_mid_click)
                    mouse.right_click(dist_pinky < 45)
                    mouse.middle_click(is_mid_click)
                    mouse.pan_3d(dist_ring < 45)

                    idx_x, idx_y = h[8][1], h[8][2]
                    if engine.is_scrolling_gesture(h):
                        mouse.trackpad_navigation(idx_x, idx_y, engine.get_finger_gap(h))
                    else:
                        mouse.prev_scroll_x = 0
                        mouse.prev_scroll_y = 0
                        mouse.move_cursor(idx_x, idx_y, cam_w, cam_h)
            else:
                mouse.rotate_3d(False)
                mouse.pan_3d(False)
                mouse.reset_all()

            overlay.update_camera_feed(frame)
            overlay.update()
            
    except KeyboardInterrupt:
        print("\nCerrando LCB-GestureControl...")

    cap.release()

if __name__ == "__main__":
    main()