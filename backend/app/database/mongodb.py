import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user_model import User


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    async def connect_to_database(self):
        """
        Connect to MongoDB database
        """
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("MONGODB_DB_NAME", "linguamentor")

        self.client = AsyncIOMotorClient(mongodb_url)
        self.database = self.client[database_name]

        # Initialize Beanie with the User document
        await init_beanie(
            database=self.database,
            document_models=[User]
        )

        print(f"Connected to MongoDB: {mongodb_url}")
        print(f"Database: {database_name}")

    async def close_database_connection(self):
        """
        Close MongoDB connection
        """
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")


# Global database instance
mongodb = MongoDB()