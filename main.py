import sys
import cv2
import mediapipe as mp

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
gc = GestureController(COOLDOWN)
ui.show()


def process_loop():
    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture_text = ""

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            x = lm.landmark[9].x * w
            y = lm.landmark[9].y * h

            gestures = ui.adapt_gestos()

            gesture = gc.detect(x, y, w, h, lm, gestures)

            if gesture:
                gesture_text = gesture

            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

    ui.update_video(frame)
    ui.update_gesture_label(gesture_text)


timer = QTimer()
timer.timeout.connect(process_loop)
timer.start(5)

sys.exit(app.exec())
