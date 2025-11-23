import cv2
import mediapipe as mp
from tkinter import Tk
from gestures import GestureController
from ui import GestureUI
from config import gestos_iniciais, COOLDOWN


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(1)
hands = mp_hands.Hands(max_num_hands=1)

root = Tk()
ui = GestureUI(root, gestos_iniciais)
gc = GestureController(COOLDOWN)

def loop():
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
            x = int(lm.landmark[9].x * w)
            y = int(lm.landmark[9].y * h)

            ui.update_video(frame)

            # CORREÇÃO AQUI:
            gestures_dict = ui.adapt_gestos()
            gesture = gc.detect(x, y, lm, gestures_dict)

            if gesture:
                gesture_text = gesture

            mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
    else:
        ui.update_video(frame)

    ui.update_gesture_label(gesture_text)
    root.after(10, loop)

root.after(0, loop)
root.mainloop()
