import time
import pyautogui


class GestureController:
    def __init__(self, cooldown=1.5, move_threshold=20,
                 zone_margin_ratio=0.15, hold_ms=150,
                 direction_tolerance=3, debug=True):

        self.cooldown = cooldown
        self.last_action = 0

        self.move_threshold = move_threshold
        self.zone_margin_ratio = zone_margin_ratio
        self.hold_ms = hold_ms
        self.direction_tolerance = direction_tolerance
        self.debug = debug

        self._start_x = None
        self._start_y = None

        self.last_x = None
        self.last_y = None

        self._gesture_start_time = None
        self._current_direction = None

        self._pinch_active = False   # gatilho de pinça

    def is_pinch(self, lm):
        """Retorna True quando polegar e indicador estão próximos."""
        # pontas dos dedos
        ix, iy = lm.landmark[8].x, lm.landmark[8].y   # indicador
        tx, ty = lm.landmark[4].x, lm.landmark[4].y   # polegar

        # distância euclidiana normalizada
        dist = ((ix - tx)**2 + (iy - ty)**2)**0.5

        return dist < 0.06  # limite ideal p/ 720p – estável para todos os gestos


    def _hard_reset(self):
        self._start_x = None
        self._start_y = None
        self._gesture_start_time = None
        self._current_direction = None


    def _soft_reset(self):
        self._gesture_start_time = None
        self._current_direction = None


    def press_keys(self, mod, key):
        if mod is None or mod == "None":
            pyautogui.press(key)
        else:
            pyautogui.hotkey(mod, key)

    def detect(self, x, y, frame_w, frame_h, landmarks=None, gestures_dict=None):
        now = time.time()

        if landmarks is None:
            return None

        pinch = self.is_pinch(landmarks)

        # ativa
        if pinch and not self._pinch_active:
            if self.debug:
                print("[DEBUG] Pinça detectada → ATIVADO")
            self._pinch_active = True
            self._hard_reset()
            return None

        # desativa
        if not pinch:
            if self._pinch_active and self.debug:
                print("[DEBUG] Pinça aberta → DESATIVADO")
            self._pinch_active = False
            self._hard_reset()
            return None

        if not self._pinch_active:
            return None

        x_min = frame_w * self.zone_margin_ratio
        x_max = frame_w * (1 - self.zone_margin_ratio)
        y_min = frame_h * self.zone_margin_ratio
        y_max = frame_h * (1 - self.zone_margin_ratio)

        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            if self.debug:
                print(f"[DEBUG] Fora da zona: ({x:.1f},{y:.1f}) → reset")
            self._hard_reset()
            self.last_x = x
            self.last_y = y
            return None

        if self._start_x is None:
            self._start_x = x
            self._start_y = y
            self.last_x = x
            self.last_y = y
            self._gesture_start_time = now * 1000

            if self.debug:
                print(f"[DEBUG] Novo gesto iniciado em ({x:.1f},{y:.1f})")
            return None

        dx_raw = x - self._start_x
        dy_raw = y - self._start_y

        dx_smooth = (dx_raw * 0.7) + ((x - self.last_x) * 0.3)
        dy_smooth = (dy_raw * 0.7) + ((y - self.last_y) * 0.3)

        direction = None
        abs_dx = abs(dx_smooth)
        abs_dy = abs(dy_smooth)

        # dominante horizontal
        if abs_dx > abs_dy * self.direction_tolerance:
            if dx_smooth > self.move_threshold:
                direction = "Seta Direita"
            elif dx_smooth < -self.move_threshold:
                direction = "Seta Esquerda"

        # dominante vertical
        elif abs_dy > abs_dx * self.direction_tolerance:
            if dy_smooth < -self.move_threshold:
                direction = "Seta Cima"
            elif dy_smooth > self.move_threshold:
                direction = "Seta Baixo"

        if self.debug:
            elapsed = (now * 1000) - (self._gesture_start_time or now * 1000)
            print(f"[DEBUG] dx={dx_smooth:.1f} dy={dy_smooth:.1f} → {direction} | {elapsed:.0f}ms")

        if direction is None:
            if (now * 1000) - self._gesture_start_time > 600:
                if self.debug:
                    print("[DEBUG] Timeout → hard reset")
                self._hard_reset()
            return None

        # direção mudou
        if self._current_direction != direction:
            if self.debug:
                print(f"[DEBUG] Mudou para {direction} → soft reset")
            self._current_direction = direction
            self._gesture_start_time = now * 1000
            self._start_x = x
            self._start_y = y
            return None

        # hold
        now_ms = now * 1000
        if now_ms - self._gesture_start_time < self.hold_ms:
            if self.debug:
                print(f"[DEBUG] Segurando {direction}: {now_ms - self._gesture_start_time:.0f}/{self.hold_ms}ms")
            return None

        # cooldown
        if now - self.last_action < self.cooldown:
            if self.debug:
                print(f"[DEBUG] Cooldown ({now - self.last_action:.2f}s)")
            self._hard_reset()
            return None

        # dispara ação
        cfg = gestures_dict.get(direction, {}) if gestures_dict else {}
        mod = cfg.get("mod")
        key = cfg.get("key")

        if key is None:
            if self.debug:
                print(f"[DEBUG] {direction} sem ação definida.")
            self._hard_reset()
            self.last_action = now
            return direction

        try:
            self.press_keys(mod, key)
            if self.debug:
                print(f"[DEBUG] Disparado {direction}: {mod}+{key}")
        except Exception as e:
            print("[DEBUG] Erro:", e)

        self.last_action = now
        self._hard_reset()
        return direction
