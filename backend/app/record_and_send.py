import sounddevice as sd
from scipy.io.wavfile import write
import requests
import json
import tempfile
import os

# --- CONFIG ---
DURATION = 10  # segundos de grabación
SAMPLE_RATE = 16000
API_URL = "http://localhost:8000/voice/analyze-voice"

def record_voice():
    print("Grabando... habla ahora (10 segs)")
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    print("Grabación finalizada.")
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_wav.name, SAMPLE_RATE, audio_data)
    return temp_wav.name

def send_to_api(wav_path):
    print(f"Enviando audio a {API_URL}")
    with open(wav_path, "rb") as f:
        files = {"file": (os.path.basename(wav_path), f, "audio/wav")}
        try:
            response = requests.post(API_URL, files=files)
            if response.status_code == 200:
                print("Feedback recibido:")
                print(json.dumps(response.json(), indent=4, ensure_ascii=False))
            else:
                print(f"Error: {response.status_code} -> {response.text}")
        except Exception as e:
            print(f"No se pudo conectar con la API: {e}")

if __name__ == "__main__":
    wav_file = record_voice()
    send_to_api(wav_file)
