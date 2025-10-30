import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import mediapipe as mp
import pyautogui
import time
from tkinter import Tk, Label, Button, Checkbutton, IntVar, Frame, StringVar
from tkinter import ttk
from PIL import Image, ImageTk


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("não foi possível abrir a câmera.")
    exit()

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

prev_x = None
last_action_time = 0
cooldown = 1.0
gesture_text = ""

root = Tk()
root.title("Gestos com Teclas e Combinações")

lbl_video = Label(root)
lbl_video.pack()

lbl_gesture = Label(root, text="", font=("Arial", 24), fg="red")
lbl_gesture.pack()

frame_controls = Frame(root)
frame_controls.pack(pady=10)

modificadores = ["None", "ctrl", "shift", "alt"]
teclas = [
    'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
    '0','1','2','3','4','5','6','7','8','9',
    'enter','space','tab','left','right','up','down','backspace','esc'
]

gestos = {
    "Seta Esquerda": {"active": IntVar(value=1), "mod": StringVar(value="None"), "key": StringVar(value="left")},
    "Seta Direita": {"active": IntVar(value=1), "mod": StringVar(value="None"), "key": StringVar(value="right")}
}

for nome, info in gestos.items():
    chk = Checkbutton(frame_controls, text=nome, variable=info["active"])
    chk.pack(anchor="w")
    
    lbl_mod = Label(frame_controls, text="Modificador:")
    lbl_mod.pack(anchor="w")
    combo_mod = ttk.Combobox(frame_controls, values=modificadores, textvariable=info["mod"], state="readonly", width=10)
    combo_mod.pack(anchor="w")
    
    lbl_key = Label(frame_controls, text="Tecla:")
    lbl_key.pack(anchor="w")
    combo_key = ttk.Combobox(frame_controls, values=teclas, textvariable=info["key"], state="readonly", width=10)
    combo_key.pack(anchor="w")
    
    ttk.Separator(frame_controls, orient='horizontal').pack(fill='x', pady=5)

btn_quit = Button(root, text="Fechar", command=root.quit)
btn_quit.pack(pady=5)

def press_keys(mod, key):
    try:
        if mod == "None":
            pyautogui.press(key)
        else:
            pyautogui.hotkey(mod, key)
    except Exception as e:
        print(f"Erro ao pressionar {mod}+{key}: {e}")

def video_loop():
    global prev_x, last_action_time, gesture_text
    ret, frame = cap.read()
    if ret:
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

                h, w, _ = frame.shape
                x = int(landmarks.landmark[9].x * w)

                if prev_x is not None:
                    diff_x = x - prev_x
                    current_time = time.time()

                    if diff_x < -50 and (current_time - last_action_time) > cooldown:
                        if gestos["Seta Esquerda"]["active"].get():
                            mod = gestos["Seta Esquerda"]["mod"].get()
                            key = gestos["Seta Esquerda"]["key"].get()
                            gesture_text = f"⬅️ {mod}+{key}" if mod!="None" else f"⬅️ {key}"
                            press_keys(mod, key)
                        last_action_time = current_time

                    elif diff_x > 50 and (current_time - last_action_time) > cooldown:
                        if gestos["Seta Direita"]["active"].get():
                            mod = gestos["Seta Direita"]["mod"].get()
                            key = gestos["Seta Direita"]["key"].get()
                            gesture_text = f"➡️ {mod}+{key}" if mod!="None" else f"➡️ {key}"
                            press_keys(mod, key)
                        last_action_time = current_time

                prev_x = x
        else:
            gesture_text = ""

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

    root.after(10, video_loop)

def update_label():
    lbl_gesture.config(text=gesture_text)
    root.after(100, update_label)

def on_closing():
    cap.release()
    hands.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.after(0, video_loop)
root.after(0, update_label)
root.mainloop()
