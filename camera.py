import cv2
import sys

cap = None

def change_camera(index):
    global cap

    if index is None or index < 0:
        print("[WARN] Índice de câmera inválido")
        return

    print(f"[DEBUG] Trocando para câmera {index}")

    if cap is not None:
        cap.release()

    # Windows
    if sys.platform == "win32":
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    # Linux
    else:
        cap = cv2.VideoCapture(index, cv2.CAP_V4L2)

    if not cap.isOpened():
        print(f"[ERRO] Câmera {index} não encontrada ou ocupada")
        cap = None
        return

    print(f"[DEBUG] Câmera {index} aberta com sucesso")

    # MJPEG costuma reduzir uso de CPU e aumentar FPS
    cap.set(
        cv2.CAP_PROP_FOURCC,
        cv2.VideoWriter_fourcc(*"MJPG")
    )

    # Tente 640x480 primeiro
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Solicita 60 FPS
    cap.set(cv2.CAP_PROP_FPS, 60)

    # Opcional: reduzir buffer para diminuir latência
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

    print("\n=== Configuração Aplicada ===")
    print("Largura :", int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
    print("Altura  :", int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print("FPS     :", cap.get(cv2.CAP_PROP_FPS))
    print("============================\n")