import os
import queue
import threading
import time
import tkinter as tk
import json
import sounddevice as sd
import vgamepad as vg
from vosk import Model, KaldiRecognizer

# Variáveis globais para configuração inicial
PALAVRA_CAVALO = " "

def iniciar_programa():
    global PALAVRA_CAVALO
    nome_digitado = entry_nome.get().strip().lower()
    if nome_digitado:
        PALAVRA_CAVALO = nome_digitado
    root_config.destroy()

# --- JANELA DE CONFIGURAÇÃO INICIAL (EM INGLÊS) ---
root_config = tk.Tk()
root_config.title("Configure Horse Command")
root_config.geometry("300x150")
root_config.resizable(False, False)

tk.Label(root_config, text="Horse name", font=("Arial", 10)).pack(pady=10)
entry_nome = tk.Entry(root_config, font=("Arial", 11), justify="center")
entry_nome.pack(pady=5, ipadx=10, ipady=3)
entry_nome.insert(0, " ")

btn_iniciar = tk.Button(root_config, text="Start WitcherVoice", command=iniciar_programa, bg="#5cb85c", fg="white", font=("Arial", 10, "bold"), width=20, height=1)
btn_iniciar.pack(pady=15)

root_config.mainloop()
# -------------------------------------

# Inicializa o controle virtual
gamepad = vg.VX360Gamepad()

# Configurações de Áudio
SAMPLE_RATE = 16000
running = True
is_casting = False

# Carrega os modelos do Vosk (Português e Inglês)
MODEL_PT_PATH = "vosk-model-small-pt-fb-0.5"
MODEL_EN_PATH = "vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PT_PATH):
  print(f"❌ Erro: A pasta do modelo em português '{MODEL_PT_PATH}' não foi encontrada!")
  exit(1)

if not os.path.exists(MODEL_EN_PATH):
  print(f"❌ Erro: A pasta do modelo em inglês '{MODEL_EN_PATH}' não foi encontrada!")
  exit(1)

print("Carregando modelos de voz (PT e EN)...")
model_pt = Model(MODEL_PT_PATH)
model_en = Model(MODEL_EN_PATH)

recognizer_pt = KaldiRecognizer(model_pt, SAMPLE_RATE)
recognizer_en = KaldiRecognizer(model_en, SAMPLE_RATE)
print(f"⚡ Sistema bilíngue pronto! Palavra do cavalo: '{PALAVRA_CAVALO}'")




def apertar_ls_duas_vezes():
  global is_casting
  is_casting = True
  print('⚡ Comando: Apertar LS 2 vezes (Cavalo)')

  try:
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gamepad.update()
    time.sleep(0.04)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gamepad.update()
    
    time.sleep(0.05)

    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gamepad.update()
    time.sleep(0.04)
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gamepad.update()
  finally:
    time.sleep(0.02)
    is_casting = False


def audio_callback(indata, frames, time_info, status):
  global is_casting
  if not running or is_casting:
    return

  audio_bytes = bytes(indata)
  text = ""

  if recognizer_pt.AcceptWaveform(audio_bytes):
    res = json.loads(recognizer_pt.Result())
    text = res.get("text", "").lower()
  
  if not text and recognizer_en.AcceptWaveform(audio_bytes):
    res = json.loads(recognizer_en.Result())
    text = res.get("text", "").lower()

  if text:
    print(f'🗣️ Reconhecido: "{text}"')
    if PALAVRA_CAVALO in text or any(w in text for w in ['horse', 'roach', 'mount']):
      apertar_ls_duas_vezes()


def audio_loop():
  with sd.RawInputStream(
      samplerate=SAMPLE_RATE,
      blocksize=8000,
      dtype='int16',
      channels=1,
      callback=audio_callback,
  ):
    while running:
      time.sleep(0.1)


# --- JANELA PRINCIPAL DE CONTROLE (EM INGLÊS) ---
root = tk.Tk()
root.title('WitcherVoice - Bilingual')
root.geometry('240x110')
root.resizable(False, False)

label = tk.Label(root, text=f'Horse: "{PALAVRA_CAVALO}"', font=('Arial', 10, 'bold'))
label.pack(pady=12)


def fechar():
  global running
  running = False
  root.destroy()


btn = tk.Button(
    root,
    text='Close',
    command=fechar,
    bg='#d9534f',
    fg='white',
    font=('Arial', 10, 'bold'),
    width=15,
    height=1,
)
btn.pack()

root.protocol('WM_DELETE_WINDOW', fechar)

t = threading.Thread(target=audio_loop)
t.daemon = True
t.start()

root.mainloop()