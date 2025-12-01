import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from config import modificadores, teclas
from gesture_config import load_gesture_config, save_gesture_config
from config import gestos_iniciais

saved = load_gesture_config()

class GestureUI:
    def __init__(self, root, gestures_data):
        self.root = root
        self.root.title("Controle por Gestos")

        self.gesture_var = tk.StringVar(value="")
        self.gestos = gestures_data

        self.video_label = tk.Label(root)
        self.video_label.pack()

        tk.Label(root, textvariable=self.gesture_var, font=("Arial", 24), fg="red").pack(pady=5)

        # Frame principal horizontal
        main_frame = tk.Frame(root)
        main_frame.pack(pady=10)

        for col_index, (nome, info) in enumerate(gestos_iniciais.items()):

            # Variáveis Tkinter
            info["active_var"] = tk.IntVar(value=info["active"])
            info["mod_var"] = tk.StringVar(value=info["mod"])
            info["key_var"] = tk.StringVar(value=info["key"])

            # Aplicar configuração salva
            if nome in saved:
                mod, key = saved[nome].split("+", 1)
                info["mod_var"].set(mod)
                info["key_var"].set(key)

            # Frame de cada gesto (coluna)
            gesture_frame = tk.Frame(main_frame, relief="raised", bd=1, padx=5, pady=5)
            gesture_frame.grid(row=0, column=col_index, padx=5, sticky="n")

            # Widgets horizontais dentro do frame
            tk.Checkbutton(gesture_frame, text=nome, variable=info["active_var"]).pack(anchor="w", pady=2)
            ttk.Combobox(gesture_frame, values=modificadores, textvariable=info["mod_var"], width=10).pack(anchor="w", pady=2)
            ttk.Combobox(gesture_frame, values=teclas, textvariable=info["key_var"], width=10).pack(anchor="w", pady=2)

    def adapt_gestos(self):
        d = {}
        for nome, info in self.gestos.items():
            d[nome] = {
                "active": info["active_var"].get(),
                "mod": info["mod_var"].get(),
                "key": info["key_var"].get()
            }
        return d

    def update_gesture_label(self, text):
        self.gesture_var.set(text)

    def update_video(self, frame_bgr):
        rgb = frame_bgr[:,:,::-1]
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)
