from fastapi import FastAPI, UploadFile, File
from .services.rabbitmq_utils import send_message
import asyncio

app = FastAPI(title="LinguaMentor Gateway")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "LinguaMentor backend funcionando"}

@app.post("/analyze_voice")
async def analyze_voice(file: UploadFile = File(...)):
    audio_data = await file.read()

    # Enviar tarea a RabbitMQ
    message = {"filename": file.filename, "size": len(audio_data)}
    await send_message("voice_analysis", message)

    return {
        "status": "processing",
        "detail": f"Archivo {file.filename} recibido y en proceso.",
    }
