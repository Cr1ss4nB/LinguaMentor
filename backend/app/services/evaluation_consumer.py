import os
import json
import asyncio
import aio_pika
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "lingua123")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_OUTPUT = "feedback_ready"

MONGO_URL = os.getenv("MONGODB_URL", "mongodb://mongo:27017")
MONGO_DB = os.getenv("MONGODB_DB_NAME", "linguamentor")

async def save_to_mongo(doc: dict):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB]
    collection = db["evaluations"]
    doc["created_at"] = datetime.utcnow()
    await collection.insert_one(doc)
    client.close()
    print("Documento guardado.")

async def consume():
    connection = await aio_pika.connect_robust(f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}/")
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(QUEUE_OUTPUT, durable=True)
        print("Evaluacion: escuchando cola", QUEUE_OUTPUT)
        queue = await channel.get_queue(QUEUE_OUTPUT)
        async with queue.iterator() as it:
            async for message in it:
                async with message.process():
                    data = json.loads(message.body)
                    try:
                        await save_to_mongo(data)
                    except Exception as e:
                        print("Error guardando en la Base de Datos:", e)

if __name__ == "__main__":
    asyncio.run(consume())
