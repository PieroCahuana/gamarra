import os
from motor.motor_asyncio import AsyncIOMotorClient

client: AsyncIOMotorClient = None
db = None


async def connect_db():
    global client, db
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[os.getenv("DB_NAME", "gamarra_db")]
    print("✅ Conectado a MongoDB Atlas")


async def close_db():
    global client
    if client:
        client.close()
        print("🔌 Conexión MongoDB cerrada")


def get_db():
    return db
