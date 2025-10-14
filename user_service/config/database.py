import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/userdb")

client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """Conectar a MongoDB"""
    global client, database
    client = AsyncIOMotorClient(MONGODB_URL)
    database = client.get_database()
    print(f"✅ Conectado a MongoDB: {MONGODB_URL}")


async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    global client
    if client:
        client.close()
        print("❌ Conexión a MongoDB cerrada")


def get_database():
    """Obtener instancia de la base de datos"""
    return database
