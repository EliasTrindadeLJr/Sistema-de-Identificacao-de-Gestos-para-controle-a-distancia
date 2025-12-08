from PySide6.QtWidgets import (
    QWidget, QLabel, QCheckBox, QComboBox,
    QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt

import cv2
from config import modificadores, teclas
from gesture_config import save_gesture_config


class GestureUI(QWidget):
    def __init__(self, gestures_data):
        super().__init__()
        self.setWindowTitle("Controle por Gestos")
        self.setMinimumSize(1100, 650)

        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QLabel#title { font-size: 28px; font-weight: bold; color: #00d4ff; }
            QLabel#gesture { font-size: 24px; color: #ff6666; font-weight: bold; }
            QFrame#card { background-color: #2a2a2a; border-radius: 12px; padding: 10px; border: 1px solid #3a3a3a; }
            QComboBox, QCheckBox { font-size: 14px; }
            QLabel#video { border: 2px solid #333; border-radius: 6px; }
        """)

        self.gestos = gestures_data

        # --- Título ---
        title_label = QLabel("Controle por Gestos")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        # --- Vídeo ---
        self.video_label = QLabel()
        self.video_label.setObjectName("video")
        self.video_label.setFixedSize(720, 480)
        self.video_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # --- Gesto detectado ---
        self.gesture_label = QLabel("Nenhum gesto detectado")
        self.gesture_label.setObjectName("gesture")
        self.gesture_label.setAlignment(Qt.AlignCenter)

        # --- Layout principal ---
        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(self.video_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.gesture_label)

        # Linha dos cards
        row = QHBoxLayout()
        row.setSpacing(20)
        layout.addLayout(row)

        # Criar widgets dos gestos
        for nome, info in self.gestos.items():

            info["active_var"] = info.get("active", True)
            info["mod_var"] = info.get("mod", "None")
            info["key_var"] = info.get("key", "")

            frame = QFrame()
            frame.setObjectName("card")
            vbox = QVBoxLayout(frame)
            vbox.setSpacing(8)

            cb = QCheckBox(nome)
            cb.setChecked(info["active_var"])
            vbox.addWidget(cb)

            combo_mod = QComboBox()
            combo_mod.addItems(modificadores)
            combo_mod.setCurrentText(info["mod_var"])
            vbox.addWidget(combo_mod)

            combo_key = QComboBox()
            combo_key.addItems(teclas)
            combo_key.setCurrentText(info["key_var"])
            vbox.addWidget(combo_key)

            info["active_widget"] = cb
            info["mod_widget"] = combo_mod
            info["key_widget"] = combo_key

            row.addWidget(frame)

    # -----------------------
    # SALVAR AO FECHAR
    # -----------------------
    def closeEvent(self, event):
        save_gesture_config(self.adapt_gestos())
        print("[DEBUG] gestures_config.json salvo.")
        event.accept()

    # --- Atualizar dicionário ---
    def adapt_gestos(self):
        d = {}
        for nome, info in self.gestos.items():
            d[nome] = {
                "active": info["active_widget"].isChecked(),
                "mod": info["mod_widget"].currentText(),
                "key": info["key_widget"].currentText()
            }
        return d

    # --- Atualizar gesto exibido ---
    def update_gesture_label(self, text):
        self.gesture_label.setText(text)

    # --- Atualizar vídeo ---
    def update_video(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))
