import time
import pyautogui


class GestureController:
    def __init__(
        self,
        cooldown=1.5,
        move_threshold=20,
        zone_margin_ratio=0.15,
        hold_ms=150,
        direction_tolerance=3,
        debug=False
    ):
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

        self._pinch_active = False

    @staticmethod
    def _get_lm(landmarks, index):
        """
        Compatível com:
        - MediaPipe Tasks API
        - MediaPipe Legacy API
        """
        try:
            return landmarks[index]
        except TypeError:
            return landmarks.landmark[index]

    def is_pinch(self, landmarks):
        """
        Retorna True quando polegar e indicador
        estão suficientemente próximos.
        """
        tip_index = self._get_lm(landmarks, 8)
        tip_thumb = self._get_lm(landmarks, 4)

        dx = tip_index.x - tip_thumb.x
        dy = tip_index.y - tip_thumb.y

        dist = (dx * dx + dy * dy) ** 0.5

        return dist < 0.06

    def _hard_reset(self):
        self._start_x = None
        self._start_y = None
        self._gesture_start_time = None
        self._current_direction = None

    def press_keys(self, mod, key):
        if mod is None or mod == "None":
            pyautogui.press(key)
        else:
            pyautogui.hotkey(mod, key)

    @property
    def pinch_active(self):
        return self._pinch_active

    def detect(
        self,
        x,
        y,
        frame_w,
        frame_h,
        landmarks=None,
        gestures_dict=None
    ):
        now = time.perf_counter()

        if landmarks is None:
            return None

        pinch = self.is_pinch(landmarks)

        # --------------------------------------------------
        # Ativação da pinça
        # --------------------------------------------------
        if pinch and not self._pinch_active:
            self._pinch_active = True
            self._hard_reset()

            if self.debug:
                print("[DEBUG] Pinça detectada → ATIVADO")

            return None

        # --------------------------------------------------
        # Desativação da pinça
        # --------------------------------------------------
        if not pinch:
            if self._pinch_active and self.debug:
                print("[DEBUG] Pinça aberta → DESATIVADO")

            self._pinch_active = False
            self._hard_reset()
            return None

        if not self._pinch_active:
            return None

        # --------------------------------------------------
        # Zona válida
        # --------------------------------------------------
        x_min = frame_w * self.zone_margin_ratio
        x_max = frame_w * (1 - self.zone_margin_ratio)

        y_min = frame_h * self.zone_margin_ratio
        y_max = frame_h * (1 - self.zone_margin_ratio)

        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            if self.debug:
                print(f"[DEBUG] Fora da zona ({x:.1f},{y:.1f})")

            self._hard_reset()

            self.last_x = x
            self.last_y = y

            return None

        # --------------------------------------------------
        # Início do gesto
        # --------------------------------------------------
        if self._start_x is None:
            self._start_x = x
            self._start_y = y

            self.last_x = x
            self.last_y = y

            self._gesture_start_time = now * 1000

            if self.debug:
                print(f"[DEBUG] Novo gesto ({x:.1f},{y:.1f})")

            return None

        # --------------------------------------------------
        # Movimento
        # --------------------------------------------------
        dx_raw = x - self._start_x
        dy_raw = y - self._start_y

        dx_frame = x - self.last_x
        dy_frame = y - self.last_y

        dx_smooth = (dx_raw * 0.7) + (dx_frame * 0.3)
        dy_smooth = (dy_raw * 0.7) + (dy_frame * 0.3)

        abs_dx = abs(dx_smooth)
        abs_dy = abs(dy_smooth)

        direction = None

        # Horizontal dominante
        if abs_dx > abs_dy * self.direction_tolerance:

            if dx_smooth > self.move_threshold:
                direction = "Seta Direita"

            elif dx_smooth < -self.move_threshold:
                direction = "Seta Esquerda"

        # Vertical dominante
        elif abs_dy > abs_dx * self.direction_tolerance:

            if dy_smooth < -self.move_threshold:
                direction = "Seta Cima"

            elif dy_smooth > self.move_threshold:
                direction = "Seta Baixo"

        # Atualiza posição anterior
        self.last_x = x
        self.last_y = y

        if self.debug:
            elapsed = (now * 1000) - (
                self._gesture_start_time or (now * 1000)
            )

            print(
                f"[DEBUG] dx={dx_smooth:.1f} "
                f"dy={dy_smooth:.1f} "
                f"dir={direction} "
                f"elapsed={elapsed:.0f}ms"
            )

        # --------------------------------------------------
        # Sem direção detectada
        # --------------------------------------------------
        if direction is None:

            if (
                self._gesture_start_time is not None
                and (now * 1000) - self._gesture_start_time > 600
            ):
                self._hard_reset()

            return None

        # --------------------------------------------------
        # Mudou de direção
        # --------------------------------------------------
        if self._current_direction != direction:

            self._current_direction = direction

            self._gesture_start_time = now * 1000

            self._start_x = x
            self._start_y = y

            return None

        # --------------------------------------------------
        # Hold
        # --------------------------------------------------
        now_ms = now * 1000

        if now_ms - self._gesture_start_time < self.hold_ms:
            return None

        # --------------------------------------------------
        # Cooldown
        # --------------------------------------------------
        if now - self.last_action < self.cooldown:
            self._hard_reset()
            return None

        # --------------------------------------------------
        # Dispara ação
        # --------------------------------------------------
        cfg = gestures_dict.get(direction, {}) if gestures_dict else {}

        mod = cfg.get("mod")
        key = cfg.get("key")

        if key is None:
            self.last_action = now
            self._hard_reset()
            return direction

        try:
            self.press_keys(mod, key)

            if self.debug:
                print(
                    f"[DEBUG] Executado: "
                    f"{mod}+{key} ({direction})"
                )

        except Exception as e:
            print("Erro ao executar ação:", e)

        self.last_action = now
        self._hard_reset()

        return direction