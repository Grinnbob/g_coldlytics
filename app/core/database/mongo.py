from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class DataBase:
    client: AsyncIOMotorClient = None
    db_name: AsyncIOMotorDatabase = None

_db = None

def connect_db():
    global _db

    if not _db:
        _db = DataBase()
        _db.client = AsyncIOMotorClient(settings.MONGODB_URI,
                                    maxPoolSize=settings.MONGODB_MAX_CONNECTIONS_COUNT,
                                    minPoolSize=settings.MONGODB_MIN_CONNECTIONS_COUNT)

        _db.db_name = _db.client[settings.MONGODB_DB_NAME]

    return _db

def close_db():
    global _db

    if _db and _db.client:
        _db.client.close()
        _db = None

def get_db() -> AsyncIOMotorDatabase:
    global _db

    if not _db:
        _db = connect_db()

    return _db.db_name