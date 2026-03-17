import sys
import os
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import HandLandmarkerOptions, HandLandmarkerResult
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gestures import GestureController
from ui import GestureUI
from config import gestos_iniciais, COOLDOWN

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

app = QApplication(sys.argv)
ui = GestureUI(gestos_iniciais)
ui.camera_changed = change_camera
gc = GestureController(COOLDOWN)
ui.show()


def process_loop():
    global frame_timestamp_ms, frame_count

    ret, frame = cap.read()
    if not ret or frame is None:
        print("[WARN] cap.read() falhou, pulando frame.")
        return

    frame_count += 1
    if frame_count <= 3:
        print(f"[DEBUG] Frame {frame_count} capturado: {frame.shape}")

    frame = cv2.flip(frame, 1)
    frame_timestamp_ms += 16

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    landmarker.detect_async(mp_image, frame_timestamp_ms)

    gesture_text = ""
    if latest_result and latest_result.hand_landmarks:
        h, w, _ = frame.shape
        for lm_list in latest_result.hand_landmarks:
            x = lm_list[9].x * w
            y = lm_list[9].y * h
            gestures = ui.adapt_gestos()
            gesture = gc.detect(x, y, w, h, lm_list, gestures)
            if gesture:
                gesture_text = gesture
        draw_landmarks(frame, latest_result.hand_landmarks)

    ui.update_video(frame)
    ui.update_gesture_label(gesture_text)


timer = QTimer()
timer.timeout.connect(process_loop)
timer.start(16)   # ~60fps
sys.exit(app.exec())