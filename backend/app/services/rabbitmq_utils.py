import aio_pika
import json
import os
import asyncio

# Variables de entorno (.env)
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "lingua123")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = "voice_analysis"

async def send_message(queue_name: str, message: dict):
    ## Envía un mensaje a RabbitMQ en la cola especificada.
    try:
        connection = await aio_pika.connect_robust(
            f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/"
        )
        async with connection:
            channel = await connection.channel()
            await channel.declare_queue(queue_name, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key=queue_name,
            )
            print(f"Mensaje enviado a {queue_name}: {message}")
    except Exception as e:
        print(f"Error: enviando mensaje a RabbitMQ: {e}")
