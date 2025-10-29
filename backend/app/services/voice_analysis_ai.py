import os
import json
import aio_pika
import asyncio
import openai
from pathlib import Path

openai.api_key = os.getenv("OPENAI_API_KEY")

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "lingua123")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

QUEUE_INPUT = "voice_analysis"
QUEUE_OUTPUT = "feedback_ready"

async def transcribe_with_whisper(path: str) -> str:
    # Usa la API OpenAI Whisper (whisper-1)
    with open(path, "rb") as f:
        resp = openai.Audio.transcriptions.create(
            file=f,
            model="whisper-1"
        )
    # resp puede variar según la versión de la API
    text = resp.get("text") if isinstance(resp, dict) else getattr(resp, "text", "")
    return text.strip()

async def analyze_with_gpt(text: str) -> str:
    prompt = (
        "Eres un tutor de idiomas. Lee la siguiente transcripción de un estudiante y "
        "genera: 1) breve corrección sugerida (una frase), 2) errores de pronunciación probables (palabras o sonidos), "
        "3) puntaje estimado de gramática y pronunciación (0-100), 4) estimación de nivel CEFR.\n\n"
        "Transcripción:\n"
        f"{text}\n\nResponde en JSON con llaves: transcription, correction, pronunciation_issues, grammar_score, pron_score, cefr, feedback_text"
    )

    resp = openai.Chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    content = resp.choices[0].message.content.strip()
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"transcription": text, "feedback_text": content}
    return parsed

async def process_and_publish(path: str, original_name: str, metadata: dict, channel):
    transcription = await transcribe_with_whisper(path)
    analysis = await analyze_with_gpt(transcription)
    result = {
        "original_name": original_name,
        "filepath": path,
        "transcription": transcription,
        "analysis": analysis,
        "metadata": metadata
    }
    body = json.dumps(result).encode()
    await channel.default_exchange.publish(
        aio_pika.Message(body=body),
        routing_key=QUEUE_OUTPUT
    )
    print("Resultado publicado en", QUEUE_OUTPUT)
    return result

async def consume():
    connection = await aio_pika.connect_robust(f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/")
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_INPUT, durable=True)
        await channel.declare_queue(QUEUE_OUTPUT, durable=True)
        print("Analizador de Voz AI: escuchando cola", QUEUE_INPUT)
        queue = await channel.get_queue(QUEUE_INPUT)
        async with queue.iterator() as it:
            async for message in it:
                async with message.process():
                    data = json.loads(message.body)
                    filepath = data.get("filepath")
                    original = data.get("original_name")
                    metadata = {"size": data.get("size", 0)}
                    if not filepath or not Path(filepath).exists():
                        print("Archivo no encontrado:", filepath)
                        continue
                    try:
                        await process_and_publish(filepath, original, metadata, channel)
                    except Exception as e:
                        print("Error en voice-analysis AI:", e)

if __name__ == "__main__":
    asyncio.run(consume())
