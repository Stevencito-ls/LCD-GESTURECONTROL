import cv2
import mediapipe as mp
import math

class GestureEngine:
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        all_hands = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                single_hand_landmarks = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # Guardamos el ID, X, Y, y la profundidad Z
                    single_hand_landmarks.append([id, cx, cy, lm.z])
                all_hands.append(single_hand_landmarks)
        return frame, all_hands

    def get_distance(self, p1, p2, landmarks):
        x1, y1 = landmarks[p1][1], landmarks[p1][2]
        x2, y2 = landmarks[p2][1], landmarks[p2][2]
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance, [x1, y1, x2, y2, (x1 + x2) // 2, (y1 + y2) // 2]

    def get_finger_gap(self, landmarks):
        dist = math.hypot(landmarks[12][1] - landmarks[8][1], landmarks[12][2] - landmarks[8][2])
        return dist < 30

    def is_scrolling_gesture(self, landmarks):
        return landmarks[8][2] < landmarks[6][2] and landmarks[12][2] < landmarks[10][2] and landmarks[16][2] > landmarks[14][2]

    def get_angle(self, p1_x, p1_y, p2_x, p2_y):
        return math.degrees(math.atan2(p2_y - p1_y, p2_x - p1_x))

    def is_hand_open(self, landmarks):
        return all([landmarks[8][2] < landmarks[6][2], landmarks[12][2] < landmarks[10][2], 
                    landmarks[16][2] < landmarks[14][2], landmarks[20][2] < landmarks[18][2]])