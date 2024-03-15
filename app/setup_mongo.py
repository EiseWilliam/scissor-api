import asyncio
from datetime import datetime
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

async def convert_all_stringtime_to_datetime_in_analytics_col():
    try:
        db = connect_to_mongo()
        log_this("Converting all string time to datetime in analytics collection.")
        async for doc in db["analytics"].find():
            if isinstance(doc["timestamp"], datetime):
                continue
            new_time = datetime.strptime(doc["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
            await db["analytics"].update_one({"_id": doc["_id"]}, {"$set": {"timestamp": new_time}})
        log_this("Converted all string time to datetime in analytics collection.")
    except Exception as e:
        log_this(f"Failed to convert all string time to datetime in analytics collection. {e}")
        sys.exit(1)
        
        
# write sccript to convert current country values to full country name and create new fields of counrty code
async def reconvert_all():
    try:
        db = connect_to_mongo()
        async for doc in db["analytics"].find():
            await db["analytics"].update_one({"_id": doc["_id"]}, {"$set": {"country": "Nigeria", "country_code":"NG"}})
        log_this("Converted all.")
    except Exception as e:
        log_this(f"Failed to convert all string time to datetime in analytics collection. {e}")
        sys.exit(1)
# async def mongo_status():
#     try:
#         await db.command("ping")
#         log_this("Mongo connection is alive.")
#     except Exception as e:
#         log_this(f"Mongo connection is down. {e}", "ERROR")
#         sys.exit(1)

if __name__ == "__main__":
    asyncio.run(reconvert_all())
    log_this("SETUP COMPLETE.", "DONE")
