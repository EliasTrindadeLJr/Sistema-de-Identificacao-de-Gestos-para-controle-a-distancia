import cv2

# Tente abrir a câmera com CAP_DSHOW
cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

# Ajusta resolução
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("❌ Erro: câmera não foi aberta.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame não capturado — tentando outro backend?")
        break

    cv2.imshow("Teste de Vídeo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()