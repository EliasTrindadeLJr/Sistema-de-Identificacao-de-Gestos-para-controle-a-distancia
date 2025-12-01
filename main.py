import cv2
import mediapipe as mp
from tkinter import Tk
from gestures import GestureController
from ui import GestureUI
from config import gestos_iniciais, COOLDOWN

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60)   # Mais suave
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

root = Tk()
ui = GestureUI(root, gestos_iniciais)
gc = GestureController(COOLDOWN)

def loop():
    ret, frame = cap.read()
    if not ret:
        root.after(10, loop)
        return
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture_text = ""

    if results.multi_hand_landmarks:
        for lm in results.multi_hand_landmarks:

            h, w, _ = frame.shape

            # Ponto base mais estável: landmark 9
            x = lm.landmark[9].x * w
            y = lm.landmark[9].y * h

            gestures_dict = ui.adapt_gestos()

            # Envia somente posição e tamanho
            gesture = gc.detect(
                x, y,
                w, h,
                lm,
                gestures_dict
            )

            if gesture:
                gesture_text = gesture

            # Desenho das landmarks
            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

    # Atualiza vídeo e label
    ui.update_video(frame)
    ui.update_gesture_label(gesture_text)

    root.after(5, loop)  # Mais responsivo

root.after(0, loop)
root.mainloop()
