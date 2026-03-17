import sys
import cv2
import os

cap = None  # variável global da câmera

def get_default_camera():
    """
    Retorna o índice e nome da câmera padrão.
    - Linux/macOS: /dev/video0
    - Windows: primeira câmera via pygrabber
    """
    if sys.platform == "win32":
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            if devices:
                return 0, devices[0]  # índice + nome
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
        cap = cv2.VideoCapture(index)  # Linux/macOS

    if not cap.isOpened():
        print(f"[ERRO] Câmera {index} não encontrada ou ocupada")
        cap = None
    else:
        print(f"[DEBUG] Câmera {index} aberta com sucesso")
        cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)