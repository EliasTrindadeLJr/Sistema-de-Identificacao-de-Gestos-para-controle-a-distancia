import gc
import time
import pyautogui
import math
from gesture_config import save_gesture_config

def pinch_distance(landmarks):
    """
    Retorna a distância entre polegar (4) e indicador (8)
    """
    x1, y1 = landmarks.landmark[4].x, landmarks.landmark[4].y
    x2, y2 = landmarks.landmark[8].x, landmarks.landmark[8].y
    return math.hypot(x2 - x1, y2 - y1)


def is_pinch_closed(landmarks, threshold=0.05):
    """Pinça fechada (ativar leitura)"""
    return pinch_distance(landmarks) < threshold


def is_pinch_open(landmarks, threshold=0.10):
    """Pinça aberta (desativar leitura)"""
    return pinch_distance(landmarks) > threshold


class GestureController:
    def __init__(self, cooldown):
        self.prev_x = None
        self.prev_y = None
        self.last_action = 0
        self.cooldown = cooldown
        
        self.reading_enabled = False
        self.last_activation = 0
        self.activation_cooldown = 1.0  # 1 segundo de proteção para não ativar/desativar sem querer

    def press_keys(self, mod, key):
        if mod == "None":
            pyautogui.press(key)
        else:
            pyautogui.hotkey(mod, key)

    def detect(self, x, y, landmarks, gestures_dict):
        gesture = None
        now = time.time()

        # Ativação/desativação da leitura
        if (now - self.last_activation) > self.activation_cooldown:

            if is_pinch_closed(landmarks):
                self.reading_enabled = True
                self.last_activation = now
                return "Leitura ativada"

            elif is_pinch_open(landmarks):
                self.reading_enabled = False
                self.last_activation = now
                return "Leitura desativada"

        # Se leitura está desativada, parar aqui
        if not self.reading_enabled:
            self.prev_x = x
            self.prev_y = y
            return None

        # Detecta movimento
        if self.prev_x is not None:
            dx = x - self.prev_x
            dy = y - self.prev_y if self.prev_y is not None else 0

            if now - self.last_action > self.cooldown:

                if dx < -50 and gestures_dict["Seta Esquerda"]["active"]:
                    gesture = "Seta Esquerda"

                elif dx > 50 and gestures_dict["Seta Direita"]["active"]:
                    gesture = "Seta Direita"

                elif dy < -50 and gestures_dict["Seta Cima"]["active"]:
                    gesture = "Seta Cima"

                elif dy > 50 and gestures_dict["Seta Baixo"]["active"]:
                    gesture = "Seta Baixo"

                if gesture:
                    mod = gestures_dict[gesture]["mod"]
                    key = gestures_dict[gesture]["key"]

                    self.press_keys(mod, key)
                    self.last_action = now

                    # SALVAR NO JSON
                    save_gesture_config({
                        nome: f'{info["mod"]}+{info["key"]}'
                        for nome, info in gestures_dict.items()
                    })

                    return gesture


        self.prev_x = x
        self.prev_y = y
        return gesture

