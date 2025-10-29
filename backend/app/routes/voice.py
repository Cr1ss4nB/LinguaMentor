from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import tempfile
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/analyze-voice")
async def analyze_voice(file: UploadFile = File(...)):
    if not file.filename.endswith(".wav"):
        raise HTTPException(status_code=400, detail="El archivo debe ser .wav")

    try:
        # Guardar el archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Transcribir con Whisper
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_path, "rb")
        )

        text = transcription.text
        print(f"🗣️ Transcripción: {text}")

        # Analizar con GPT-4o-mini
        prompt = f"""
        Eres un tutor de pronunciación y gramática. Evalúa el texto siguiente:
        '{text}'
        Da feedback breve sobre:
        - Errores de pronunciación probables
        - Corrección gramatical
        - Nivel aproximado (A1–C2)
        """

        feedback = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )

        analysis = feedback.choices[0].message.content

        return {
            "transcription": text,
            "feedback": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
