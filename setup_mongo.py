import asyncio
import sys

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config.settings import settings
from app.core.logging import log_this


# conncect to mongo
def connect_to_mongo():
    try:
        db = AsyncIOMotorClient(settings.MONGO_URI)[settings.MONGO_DB]
        log_this("Connected to mongo.")
    except Exception as e:
        log_this(f"Failed to connect to mongo. {e}")
        sys.exit(1)
    return db


# create and index collections
async def setup_mongo():
    try:
        db = connect_to_mongo()
        log_this("Creating collections and indexing.")
        await db["urls"].create_index("short_url", unique=True)

        await db["users"].create_index("email", unique=True)

        await db["analytics"].create_index(["short_url", "timestamp"])
        log_this("Created indexes.")
    except Exception as e:
        log_this(f"Failed to create indexes. {e}")
        sys.exit(1)


# async def mongo_status():
#     try:
#         await db.command("ping")
#         log_this("Mongo connection is alive.")
#     except Exception as e:
#         log_this(f"Mongo connection is down. {e}", "ERROR")
#         sys.exit(1)

if __name__ == "__main__":
    asyncio.run(setup_mongo())
    log_this("SETUP COMPLETE.", "DONE")
