import aio_pika
import asyncio
import json
import os

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "lingua123")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = "voice_analysis"

async def process_voice(message: dict):
    filename = message.get("filename", "unknown.wav")
    print(f"Analizando archivo {filename}...")
    await asyncio.sleep(2)  # Simula tiempo de procesamiento
    print(f"Resultado: pronunciación buena, gramática aceptable.\n")

async def consume_messages():
    ## Conecta con RabbitMQ y procesa mensajes de la cola 'voice_analysis'.
    try:
        connection = await aio_pika.connect_robust(
            f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
        )
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(RABBITMQ_QUEUE, durable=True)
            print(f"Escuchando mensajes en la cola '{RABBITMQ_QUEUE}'...")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        data = json.loads(message.body)
                        await process_voice(data)

    except Exception as e:
        print(f"Error al consumir mensajes: {e}")

if __name__ == "__main__":
    asyncio.run(consume_messages())
