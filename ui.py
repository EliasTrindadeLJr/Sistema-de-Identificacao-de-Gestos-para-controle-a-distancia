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
        self.resize(1280, 720)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QLabel#title { font-size: 28px; font-weight: bold; color: #00d4ff; }
            QLabel#gesture { font-size: 24px; color: #ff6666; font-weight: bold; }
            QFrame#card { background-color: #2a2a2a; border-radius: 12px; padding: 10px; border: 1px solid #3a3a3a; }
            QComboBox, QCheckBox { font-size: 14px; }
            QLabel#video { background-color: #000; border: 2px solid #333; border-radius: 6px; }
        """)
        self.gestos = gestures_data
        self._first_frame = True

        title_label = QLabel("Controle por Gestos")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(40)

        self.video_label = QLabel("Aguardando câmera...")
        self.video_label.setObjectName("video")
        self.video_label.setFixedSize(854, 480)   # 16:9 fixo — garante espaço antes do 1º frame
        self.video_label.setAlignment(Qt.AlignCenter)

        self.gesture_label = QLabel("Nenhum gesto detectado")
        self.gesture_label.setObjectName("gesture")
        self.gesture_label.setAlignment(Qt.AlignCenter)
        self.gesture_label.setFixedHeight(36)

        # ── Cards de configuração ──────────────────────────────────────────
        row = QHBoxLayout()
        row.setSpacing(20)

        for nome, info in self.gestos.items():
            info["active_var"] = info.get("active", True)
            info["mod_var"]    = info.get("mod", "None")
            info["key_var"]    = info.get("key", "")

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
            info["mod_widget"]    = combo_mod
            info["key_widget"]    = combo_key

            row.addWidget(frame)

        # ── Layout principal ───────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(self.video_label, alignment=Qt.AlignHCenter)
        layout.addWidget(self.gesture_label)
        layout.addLayout(row)

    # ── Eventos ───────────────────────────────────────────────────────────────
    def closeEvent(self, event):
        save_gesture_config(self.adapt_gestos())
        print("[DEBUG] gestures_config.json salvo.")
        event.accept()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def adapt_gestos(self):
        d = {}
        for nome, info in self.gestos.items():
            d[nome] = {
                "active": info["active_widget"].isChecked(),
                "mod":    info["mod_widget"].currentText(),
                "key":    info["key_widget"].currentText(),
            }
        return d

    def update_gesture_label(self, text):
        if text:
            self.gesture_label.setText(text)

    def update_video(self, frame_bgr):
        if self._first_frame:
            print(f"[DEBUG UI] Primeiro frame recebido: {frame_bgr.shape}")
            self._first_frame = False

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        if pixmap.isNull():
            print("[DEBUG UI] Pixmap nulo!")
            return

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )