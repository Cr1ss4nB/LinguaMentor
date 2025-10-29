import os
import json
import aio_pika
import asyncio
from pathlib import Path
from openai import OpenAI

# 🔹 Inicializar cliente OpenAI con la API key del entorno
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "lingua123")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

QUEUE_INPUT = "voice_analysis"
QUEUE_OUTPUT = "feedback_ready"

async def transcribe_with_whisper(path: str) -> str:
    """Transcribe un archivo de audio usando el modelo Whisper-1"""
    with open(path, "rb") as f:
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    text = getattr(resp, "text", "").strip()
    return text


async def analyze_with_gpt(text: str) -> dict:
    """Analiza pronunciación y gramática usando GPT-4o-mini"""
    prompt = (
        "Eres un tutor de idiomas. Lee la siguiente transcripción de un estudiante y "
        "genera: 1) una breve corrección sugerida (una frase), "
        "2) posibles errores de pronunciación (palabras o sonidos), "
        "3) puntaje estimado de gramática y pronunciación (0-100), "
        "4) nivel CEFR (A1–C2).\n\n"
        f"Transcripción:\n{text}\n\n"
        "Responde en JSON con las llaves: "
        "transcription, correction, pronunciation_issues, grammar_score, pron_score, cefr, feedback_text"
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = resp.choices[0].message.content.strip()

    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"transcription": text, "feedback_text": content}

    return parsed

async def process_and_publish(path: str, original_name: str, metadata: dict, channel):
    print(f"Procesando archivo: {original_name}")

    transcription = await transcribe_with_whisper(path)
    analysis = await analyze_with_gpt(transcription)

    result = {
        "original_name": original_name,
        "filepath": path,
        "transcription": transcription,
        "analysis": analysis,
        "metadata": metadata,
    }

    body = json.dumps(result, ensure_ascii=False).encode()

    await channel.default_exchange.publish(
        aio_pika.Message(body=body),
        routing_key=QUEUE_OUTPUT,
    )

    print(f"Resultado publicado en la cola '{QUEUE_OUTPUT}'")
    return result


async def consume():    
    url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
    print(f"Conectando a RabbitMQ en {url}")

    connection = await aio_pika.connect_robust(url)

    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_INPUT, durable=True)
        await channel.declare_queue(QUEUE_OUTPUT, durable=True)

        print(f"Analizador de Voz AI escuchando cola: {QUEUE_INPUT}")
        queue = await channel.get_queue(QUEUE_INPUT)

        async with queue.iterator() as it:
            async for message in it:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        filepath = data.get("filepath")
                        original = data.get("original_name")
                        metadata = {"size": data.get("size", 0)}

                        if not filepath or not Path(filepath).exists():
                            print(f"Archivo no encontrado: {filepath}")
                            continue

                        await process_and_publish(filepath, original, metadata, channel)
                    except Exception as e:
                        print(f"Error procesando mensaje: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        print("Servicio Voice AI detenido manualmente")
