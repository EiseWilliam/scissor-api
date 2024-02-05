from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config.settings import settings

URI = settings.MONGO_URI
DB = settings.MONGO_DB
# class MongoManager:
#     def __init__(self, uri: str = URI):
#         self.db = AsyncIOMotorClient(URI)


#     def __enter__(self) -> AsyncIOMotorDatabase:
#         return self.db["price_tracker"]


#     def __exit__(self, exc_type, exc_value, traceback):
#         self.db.close()

# def get_db() -> Any:
#     with MongoManager() as db:
#         print("Connected to mongo.")
#         yield db
#         print("Mongo connection closed.")

db = AsyncIOMotorClient(URI).DB

# create analytics collection

