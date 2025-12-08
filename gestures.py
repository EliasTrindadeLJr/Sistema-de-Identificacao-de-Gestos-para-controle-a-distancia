import time
import pyautogui

class GestureController:
    def __init__(self, cooldown=1.5, move_threshold=22,zone_margin_ratio=0.10, hold_ms=200, debug=True):
        self.cooldown = cooldown
        self.last_action = 0

        # valor mínimo de movimento para contar como gesto (em px ou unidade do frame)
        self.move_threshold = move_threshold

        # posição inicial do gesto (não atualizar toda frame)
        self._start_x = None
        self._start_y = None

        # ultima leitura bruta (opcional, só para debug/visual)
        self.last_x = None
        self.last_y = None

        # zona de detecção (fracao do frame)
        self.zone_margin_ratio = zone_margin_ratio

        # tempo mínimo que o movimento deve permanecer para disparar (ms)
        self.hold_ms = hold_ms
        self._gesture_start_time = None
        self._current_direction = None

        # debug flag
        self.debug = debug

    def press_keys(self, mod, key):
        if mod == "None" or mod is None:
            pyautogui.press(key)
        else:
            pyautogui.hotkey(mod, key)

    def _reset_gesture(self):
        self._start_x = None
        self._start_y = None
        self._gesture_start_time = None
        self._current_direction = None

    def detect(self, x, y, frame_w, frame_h, landmarks=None, gestures_dict=None):
        """
        Retorna a direção disparada (string) ou None.
        gestures_dict deve ser um dict com chaves "Seta Direita"/"Seta Esquerda"/... e valores com "active","mod","key".
        """
        now = time.time()

        # 1) delimitar zona de deteccao
        x_min = frame_w * self.zone_margin_ratio
        x_max = frame_w * (1 - self.zone_margin_ratio)
        y_min = frame_h * self.zone_margin_ratio
        y_max = frame_h * (1 - self.zone_margin_ratio)

        # se fora da zona, resetar o estado do gesto (não iniciar)
        if not (x_min <= x <= x_max and y_min <= y <= y_max):
            if self.debug:
                print(f"[DEBUG] Fora da zona: ({x:.1f},{y:.1f}) -> reset")
            self._reset_gesture()
            self.last_x = x
            self.last_y = y
            return None

        # iniciar gesto quando não temos ponto inicial
        if self._start_x is None:
            self._start_x = x
            self._start_y = y
            self._gesture_start_time = now * 1000  # ms
            self.last_x = x
            self.last_y = y
            if self.debug:
                print(f"[DEBUG] Gesto iniciado em ({x:.1f},{y:.1f}) t={self._gesture_start_time:.0f}ms")
            return None

        # calcular deslocamento acumulado desde o inicio do gesto
        dx = x - self._start_x
        dy = y - self._start_y

        # detectar direção baseada no deslocamento acumulado
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

        if self.debug:
            elapsed = (now * 1000) - (self._gesture_start_time or now*1000)
            print(f"[DEBUG] dx={dx:.1f}, dy={dy:.1f}, dir={direction}, elapsed={elapsed:.0f}ms")

        # se nenhum movimento significativo ainda -> manter estado (não resetar), permitir acumular
        if not direction:
            # opcional: se o usuário ficar muito tempo sem movimento relevante, resetar
            if (now * 1000) - (self._gesture_start_time or now*1000) > 1500:
                # muito tempo sem completar gesto -> reset
                if self.debug:
                    print("[DEBUG] Timeout sem completar gesto -> reset")
                self._reset_gesture()
            return None

        # se direção detectada mas gestures_dict diz que está inativa -> reset para novo gesto
        if gestures_dict is not None and not gestures_dict.get(direction, {"active": False})["active"]:
            if self.debug:
                print(f"[DEBUG] Direção {direction} inativa nas configurações -> reset")
            self._reset_gesture()
            return None

        # se direção mudou, não disparamos imediatamente: atualizamos current_direction e aguardamos hold
        if self._current_direction != direction:
            self._current_direction = direction
            # reiniciar o timer de hold a partir do momento que a direção fica consistente
            self._gesture_start_time = now * 1000
            if self.debug:
                print(f"[DEBUG] Direção mudou para {direction}, iniciando hold t={self._gesture_start_time:.0f}ms")
            return None

        # verificar hold time
        now_ms = now * 1000
        if now_ms - self._gesture_start_time < self.hold_ms:
            # ainda segurando
            if self.debug:
                print(f"[DEBUG] Hold não completo: {now_ms - self._gesture_start_time:.0f}ms / {self.hold_ms}ms")
            return None

        # verificar cooldown entre ações
        if now - self.last_action < self.cooldown:
            if self.debug:
                print(f"[DEBUG] Em cooldown ({now - self.last_action:.2f}s) -> ignorando")
            # após ignorar, vamos resetar o gesto para evitar múltiplos disparos
            self._reset_gesture()
            return None

        # tudo ok -> disparar a tecla
        mod = None
        key = None
        if gestures_dict is not None:
            cfg = gestures_dict.get(direction, {})
            mod = cfg.get("mod")
            key = cfg.get("key")
        if key is None:
            # se não recebeu config, apenas retorna a direção (útil pra debug)
            if self.debug:
                print(f"[DEBUG] Ação para {direction} não configurada. Retornando direção.")
            self._reset_gesture()
            self.last_action = now
            return direction

        # executar ação
        try:
            self.press_keys(mod, key)
            if self.debug:
                print(f"[DEBUG] Disparado {mod}+{key} para {direction}")
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Erro ao pressionar tecla: {e}")

        self.last_action = now

        # resetar para próximo gesto
        self._reset_gesture()

        return direction