# 👋 Controle por Gestos com OpenCV e MediaPipe

Este projeto utiliza **OpenCV**, **MediaPipe** e **PyAutoGUI** para detectar movimentos com a webcam e realizar ações no computador, como controlar o mouse ou interagir com o sistema usando gestos das mãos.

---

## 🧠 Tecnologias Utilizadas

- [Python 3.10](https://www.python.org/downloads/release/python-3100/)
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)
- [time](https://docs.python.org/3/library/time.html) (módulo padrão do Python)

---

## ⚙️ Instalação e Configuração

### 1️⃣ Clonar o Repositório


git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

### 2️⃣ Criar o Ambiente Virtual (venv)

Instalar python 3.10 

Crie e ative o ambiente virtual com Python 3.10:
Windows

py -3.10 -m venv venv
venv\Scripts\activate

Linux / macOS

python3.10 -m venv venv
source venv/bin/activate

### 3️⃣ Instalar Dependências

Crie um arquivo requirements.txt com o seguinte conteúdo:

opencv-python
mediapipe
pyautogui

E depois execute:

pip install -r requirements.txt

### ▶️ Como Executar

Após ativar o ambiente virtual e instalar as dependências, execute o script principal (por exemplo, main.py):

python main.py

Certifique-se de que sua webcam está conectada e funcionando.
