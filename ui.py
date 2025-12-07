from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QCheckBox, QComboBox,
    QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

import cv2
from config import modificadores, teclas, gestos_iniciais
from gesture_config import load_gesture_config

saved = load_gesture_config()


class GestureUI(QWidget):
    def __init__(self, gestures_data):
        super().__init__()
        self.setWindowTitle("Controle por Gestos")
        self.setMinimumSize(1100, 650)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI';
            }
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #00d4ff;
            }
            QLabel#gesture {
                font-size: 24px;
                color: #ff6666;
                font-weight: bold;
            }
            QFrame#card {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 10px;
                border: 1px solid #3a3a3a;
            }
            QComboBox, QCheckBox {
                font-size: 14px;
            }
            QLabel#video {
                border: 2px solid #333;
                border-radius: 6px;
            }
        """)

        self.gestos = gestures_data

        # --- TÍTULO ---
        title_label = QLabel("Controle por Gestos")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        # --- VÍDEO ---
        self.video_label = QLabel()
        self.video_label.setObjectName("video")
        self.video_label.setFixedSize(720, 480)
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # --- LABEL DO GESTO ---
        self.gesture_label = QLabel("Nenhum gesto detectado")
        self.gesture_label.setObjectName("gesture")
        self.gesture_label.setAlignment(Qt.AlignCenter)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.gesture_label)

        # Linha dos cards
        main_row = QHBoxLayout()
        main_row.setSpacing(20)
        layout.addLayout(main_row)

        # Criar widgets dos gestos (como cards)
        for nome, info in gestos_iniciais.items():

            info["active_var"] = info.get("active", 0)
            info["mod_var"] = info.get("mod", "")
            info["key_var"] = info.get("key", "")

            if nome in saved:
                mod, key = saved[nome].split("+", 1)
                info["mod_var"] = mod
                info["key_var"] = key

            # --- CARD DO GESTO ---
            frame = QFrame()
            frame.setObjectName("card")
            vbox = QVBoxLayout(frame)
            vbox.setSpacing(10)

            # CheckBox
            cb = QCheckBox(nome)
            cb.setChecked(info["active_var"])
            vbox.addWidget(cb)

            # Combo modificador
            combo_mod = QComboBox()
            combo_mod.addItems(modificadores)
            combo_mod.setCurrentText(info["mod_var"])
            vbox.addWidget(combo_mod)

            # Combo tecla
            combo_key = QComboBox()
            combo_key.addItems(teclas)
            combo_key.setCurrentText(info["key_var"])
            vbox.addWidget(combo_key)

            # Guardar widgets
            info["active_widget"] = cb
            info["mod_widget"] = combo_mod
            info["key_widget"] = combo_key

            main_row.addWidget(frame)

    # --- Funções da UI ---
    def adapt_gestos(self):
        d = {}
        for nome, info in self.gestos.items():
            d[nome] = {
                "active": info["active_widget"].isChecked(),
                "mod": info["mod_widget"].currentText(),
                "key": info["key_widget"].currentText()
            }
        return d

    def update_gesture_label(self, text: str):
        self.gesture_label.setText(text)

    def update_video(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))
