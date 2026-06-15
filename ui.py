from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
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
        self.resize(1400, 1000)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
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

            QLabel#pinch {
                font-size: 18px;
                font-weight: bold;
            }

            QFrame#card {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 10px;
                border: 1px solid #3a3a3a;
            }

            QComboBox,
            QCheckBox {
                font-size: 14px;
            }

            QLabel#video {
                background-color: #000;
                border: 2px solid #333;
                border-radius: 6px;
            }
        """)

        self.gestos = gestures_data
        self._first_frame = True

        # -------------------------------------------------
        # Título
        # -------------------------------------------------

        title_label = QLabel("Controle por Gestos")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)

        # -------------------------------------------------
        # Vídeo
        # -------------------------------------------------

        self.video_label = QLabel("Aguardando câmera...")
        self.video_label.setObjectName("video")
        self.video_label.setFixedSize(1280, 720)
        self.video_label.setAlignment(Qt.AlignCenter)

        # -------------------------------------------------
        # Label do gesto
        # -------------------------------------------------

        self.gesture_label = QLabel("Nenhum gesto detectado")
        self.gesture_label.setObjectName("gesture")
        self.gesture_label.setAlignment(Qt.AlignCenter)

        # -------------------------------------------------
        # Indicador de pinça
        # -------------------------------------------------

        self.pinch_label = QLabel("🔴 Pinça INATIVA")
        self.pinch_label.setObjectName("pinch")
        self.pinch_label.setAlignment(Qt.AlignCenter)
        self.pinch_label.setStyleSheet("""
            color: #ff4444;
            font-size: 18px;
            font-weight: bold;
        """)

        # -------------------------------------------------
        # Cartões de configuração
        # -------------------------------------------------

        row = QHBoxLayout()
        row.setSpacing(20)

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

            combo_mod = QComboBox()
            combo_mod.addItems(modificadores)
            combo_mod.setCurrentText(info["mod_var"])

            combo_key = QComboBox()
            combo_key.addItems(teclas)
            combo_key.setCurrentText(info["key_var"])

            vbox.addWidget(cb)
            vbox.addWidget(combo_mod)
            vbox.addWidget(combo_key)

            info["active_widget"] = cb
            info["mod_widget"] = combo_mod
            info["key_widget"] = combo_key

            row.addWidget(frame)

        # -------------------------------------------------
        # Layout principal
        # -------------------------------------------------

        layout = QVBoxLayout(self)

        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(title_label)

        layout.addWidget(
            self.video_label,
            alignment=Qt.AlignHCenter
        )

        layout.addWidget(self.gesture_label)
        layout.addWidget(self.pinch_label)

        layout.addLayout(row)

    # -----------------------------------------------------
    # Fechamento
    # -----------------------------------------------------

    def closeEvent(self, event):
        save_gesture_config(self.adapt_gestos())
        print("[DEBUG] gestures_config.json salvo.")
        event.accept()

    # -----------------------------------------------------
    # Configuração dos gestos
    # -----------------------------------------------------

    def adapt_gestos(self):
        d = {}

        for nome, info in self.gestos.items():
            d[nome] = {
                "active": info["active_widget"].isChecked(),
                "mod": info["mod_widget"].currentText(),
                "key": info["key_widget"].currentText(),
            }

        return d

    # -----------------------------------------------------
    # Atualização do texto do gesto
    # -----------------------------------------------------

    def update_gesture_label(self, text):
        if text:
            self.gesture_label.setText(text)

    # -----------------------------------------------------
    # Atualização do indicador de pinça
    # -----------------------------------------------------

    def update_pinch_status(self, active):

        if active:
            self.pinch_label.setText("🟢 Pinça ATIVA")

            self.pinch_label.setStyleSheet("""
                color: #00ff66;
                font-size: 18px;
                font-weight: bold;
            """)
        else:
            self.pinch_label.setText("🔴 Pinça INATIVA")

            self.pinch_label.setStyleSheet("""
                color: #ff4444;
                font-size: 18px;
                font-weight: bold;
            """)

    # -----------------------------------------------------
    # Atualização do vídeo
    # -----------------------------------------------------

    def update_video(self, frame_bgr):

        if self._first_frame:
            print(
                f"[DEBUG UI] Primeiro frame recebido: "
                f"{frame_bgr.shape}"
            )
            self._first_frame = False

        rgb = cv2.cvtColor(
            frame_bgr,
            cv2.COLOR_BGR2RGB
        )

        h, w, ch = rgb.shape

        qimg = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(qimg)

        if pixmap.isNull():
            print("[DEBUG UI] Pixmap nulo!")
            return

        pixmap = pixmap.scaled(
            self.video_label.width(),
            self.video_label.height(),
            Qt.KeepAspectRatioByExpanding,
            Qt.FastTransformation
        )

        self.video_label.setPixmap(pixmap)