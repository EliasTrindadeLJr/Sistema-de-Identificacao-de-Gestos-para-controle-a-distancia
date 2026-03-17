# main.py
import sys
import os
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import HandLandmarkerOptions, HandLandmarkerResult
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from gestures import GestureController
from ui import GestureUI
from config import gestos_iniciais, COOLDOWN

# ---------- Modelo Mediapipe ----------
MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print(f"[INFO] Baixando modelo...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("[INFO] Download concluído.")

# ---------- Variável global da câmera ----------
cap = None

# ---------- Funções de câmera ----------
def get_default_camera():
    """Retorna (índice, nome) da câmera padrão."""
    if sys.platform == "win32":
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            if devices:
                return 0, devices[0]
        except Exception as e:
            print(f"[ERRO] PyGrabber não disponível: {e}")
            return None
    else:
        default_dev = "/dev/video0"
        if os.path.exists(default_dev):
            return 0, default_dev
    return None

def change_camera(index):
    global cap
    if index is None or index < 0:
        print("[WARN] Índice de câmera inválido")
        return

    print(f"[DEBUG] Trocando para câmera {index}")

    if cap:
        cap.release()

    if sys.platform == "win32":
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(index)

    if not cap.isOpened():
        print(f"[ERRO] Câmera {index} não encontrada ou ocupada")
        cap = None
    else:
        print(f"[DEBUG] Câmera {index} aberta com sucesso")
        cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ---------- Inicializa câmera ----------
default_cam = get_default_camera()
if default_cam:
    cam_index, cam_name = default_cam
    print("Câmera padrão:", cam_index, cam_name)
    change_camera(cam_index)
else:
    print("[ERRO] Nenhuma câmera disponível")
    sys.exit(1)

ret, test_frame = cap.read()
if not ret or test_frame is None:
    print("[ERRO] cap.read() falhou. Câmera pode estar ocupada")
    sys.exit(1)
print(f"[DEBUG] Câmera OK — frame shape: {test_frame.shape}")

# ---------- Configurações Mediapipe ----------
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]

latest_result: HandLandmarkerResult | None = None # type: ignore

def result_callback(result, output_image, timestamp_ms):
    global latest_result
    latest_result = result

options = HandLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp_vision.RunningMode.LIVE_STREAM,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6,
    result_callback=result_callback,
)
landmarker = mp_vision.HandLandmarker.create_from_options(options)

# ---------- Inicializa UI ----------
app = QApplication(sys.argv)
ui = GestureUI(gestos_iniciais)
ui.camera_changed = change_camera
gc = GestureController(COOLDOWN)
ui.show()
app.processEvents()
print("[DEBUG] UI exibida.")

# ---------- Funções de desenho e loop ----------
frame_timestamp_ms = 0
frame_count = 0

def draw_landmarks(frame, hand_landmarks_list):
    h, w, _ = frame.shape
    for lm_list in hand_landmarks_list:
        pts = [(int(lm.x * w), int(lm.y * h)) for lm in lm_list]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (255, 255, 255), 2)
        for pt in pts:
            cv2.circle(frame, pt, 4, (0, 255, 0), -1)

def process_loop():
    global frame_timestamp_ms, frame_count

    if cap is None:
        return

    ret, frame = cap.read()
    if not ret or frame is None:
        print("[WARN] cap.read() falhou, pulando frame.")
        return

    frame_count += 1
    if frame_count <= 3:
        print(f"[DEBUG] Frame {frame_count} capturado: {frame.shape}")

    frame = cv2.flip(frame, 1)
    frame_timestamp_ms += 16

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    landmarker.detect_async(mp_image, frame_timestamp_ms)

    gesture_text = ""
    if latest_result and latest_result.hand_landmarks:
        h, w, _ = frame.shape
        for lm_list in latest_result.hand_landmarks:
            x = lm_list[9].x * w
            y = lm_list[9].y * h
            gestures = ui.adapt_gestos()
            gesture = gc.detect(x, y, w, h, lm_list, gestures)
            if gesture:
                gesture_text = gesture
        draw_landmarks(frame, latest_result.hand_landmarks)

    ui.update_video(frame)
    ui.update_gesture_label(gesture_text)

# ---------- Timer para loop de captura ----------
timer = QTimer()
timer.timeout.connect(process_loop)
timer.start(16)  # ~60fps

sys.exit(app.exec())