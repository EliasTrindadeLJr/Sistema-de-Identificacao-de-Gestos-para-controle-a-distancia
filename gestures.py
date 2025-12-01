import time
import pyautogui

class GestureController:
    def __init__(self, cooldown=0.45, move_threshold=20,
                 zone_margin_ratio=0.2, hold_ms=100):
        self.cooldown = cooldown
        self.last_action = 0

        # valor mínimo de movimento para contar como gesto
        self.move_threshold = move_threshold

        # última posição registrada
        self.last_x = None
        self.last_y = None

        # zona de detecção (fracao do frame)
        self.zone_margin_ratio = zone_margin_ratio

        # tempo mínimo que o movimento deve permanecer para disparar (ms)
        self.hold_ms = hold_ms
        self._gesture_start_time = None
        self._current_direction = None

    def press_keys(self, mod, key):
        if mod == "None":
            pyautogui.press(key)
        else:
            pyautogui.hotkey(mod, key)

    def detect(self, x, y, frame_w, frame_h, landmarks, gestures_dict):
        now = time.time()

        # -----------------------
        # 1️⃣ DELIMITAR ZONA DE DETECÇÃO
        # -----------------------
        x_min = frame_w * self.zone_margin_ratio
        x_max = frame_w * (1 - self.zone_margin_ratio)
        y_min = frame_h * self.zone_margin_ratio
        y_max = frame_h * (1 - self.zone_margin_ratio)

        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            # fora da zona: resetar timer
            self._gesture_start_time = None
            self._current_direction = None
            self.last_x = x
            self.last_y = y
            return None

        # primeira leitura: apenas armazena
        if self.last_x is None:
            self.last_x = x
            self.last_y = y
            return None

        # -----------------------
        # 2️⃣ DIFERENÇA DE MOVIMENTO
        # -----------------------
        dx = x - self.last_x
        dy = y - self.last_y
        self.last_x = x
        self.last_y = y

        # detectar direção
        direction = None
        if abs(dx) > abs(dy):
            if dx > self.move_threshold:
                direction = "Seta Direita"
            elif dx < -self.move_threshold:
                direction = "Seta Esquerda"
        else:
            if dy < -self.move_threshold:
                direction = "Seta Cima"
            elif dy > self.move_threshold:
                direction = "Seta Baixo"

        if not direction or not gestures_dict[direction]["active"]:
            # resetar temporizador se movimento não válido
            self._gesture_start_time = None
            self._current_direction = None
            return None

        # -----------------------
        # 3️⃣ HOLD / HISterese
        # -----------------------
        now_ms = now * 1000
        if self._current_direction != direction:
            # nova direção: iniciar temporizador
            self._gesture_start_time = now_ms
            self._current_direction = direction
            return None

        if now_ms - self._gesture_start_time < self.hold_ms:
            # movimento ainda não durou o suficiente
            return None

        # -----------------------
        # cooldown
        # -----------------------
        if now - self.last_action < self.cooldown:
            return None

        # dispara tecla
        mod = gestures_dict[direction]["mod"]
        key = gestures_dict[direction]["key"]
        self.press_keys(mod, key)
        self.last_action = now

        # resetar hold para próxima detecção
        self._gesture_start_time = None
        self._current_direction = None

        return direction
