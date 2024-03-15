from typing import Any

from bson import ObjectId
from linkpreview import link_preview
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.db.database import db
from app.core.exceptions import ConflictException, NotFoundException, ForbiddenException, URLNotFoundException
from app.core.logging import log_this
from app.core.utils.url import hash_url
from app.schemas.url import ListUrl, Url, UrlAnalyticsResponse
from app.services.base_crud import BaseCRUD
import random
import string

from app.services.tasks import populate_preview


class UrlHandler(BaseCRUD):
    def __init__(self, db_conn: AsyncIOMotorDatabase):  # type: ignore
        super().__init__(db_conn, "urls")
        self.redis = Redis(decode_responses=True)

        
    async def get_url_details(self, short_url: str) -> Url | None:
        result = await self.get(short_url = short_url)
        if result:
            return Url(**result)
    
    async def get_url_stats(self, short_url: str) -> UrlAnalyticsResponse:
        result = await self._db_conn.get_collection("analytics").find({"short_url": short_url}).to_list(None)
        if result:
            return UrlAnalyticsResponse(
                activities=result,
                total_clicks=len(result),
                last_clicked=result[-1].get("timestamp") if result else None,
            )
        raise NotFoundException(f"No analytics found for {short_url}")

    async def get_user_urls(self, user_id: str | ObjectId):
        return ListUrl(
            urls = await self._db_conn.get_collection(self._collection).find({"user_id": user_id}).to_list(None)
        )
    async def get_user_recent_urls(self, user_id: str | ObjectId, limit: int = 5):
        return ListUrl(
            urls = await self._db_conn.get_collection(self._collection).find({"user_id": user_id}).sort([("created_at", -1)]).to_list(limit)
        ).model_dump()
    async def _cache_url_mapping(self, short_url: str, original_url: str) -> None:
        await self.redis.set(short_url, original_url)
        
    async def _url_from_cache(self, short_url: str) -> str:
        return await self.redis.get(short_url)

    async def get_original_url(self, short_url: str):
        original_url = await self._url_from_cache(short_url)
        if original_url is None:
            log_this(f"Cache miss for {short_url}. Fetching from DB.")
            doc = await self._db_conn.get_collection(self._collection).find_one({"short_url": short_url})
            if doc:
                original_url = doc["original_url"]
                await self._cache_url_mapping(short_url, original_url)
                return original_url
            else:
                raise URLNotFoundException
        return original_url
        
    async def _is_owner(self, short_url:str, user_id: str) -> bool:
        res = await self._db_conn.get_collection(self._collection).find_one({"short_url": short_url, "user_id": user_id})
        if res:
            return True
        return False
        
    async def update_url(self, short_url: str,user_id:str | ObjectId, **kwargs):
        if self._is_owner(short_url, str(user_id)):
            res = await self._db_conn.get_collection(self._collection).update_one({"short_url": short_url}, {"$set": kwargs})
            if res.acknownledged:
                return True
        raise ForbiddenException("You are not the owner of this URL")
    
    async def delete_url(self,short_url: str,user_id:str | ObjectId, **kwargs):
        if self._is_owner(short_url, str(user_id)):
            res = await self._db_conn.get_collection(self._collection).delete_one({"short_url": short_url})
            if res.acknownledged:
                return True
        raise ForbiddenException("You are not the owner of this URL")
   
    async def custom_alias_is_available(self, alias: str) -> bool:
       return not await self._collision_check(alias)
    
    async def shorten_url(self, user_id: str | ObjectId, original_url: str, custom_alias: str | None = None, **kwargs):
        if custom_alias:
            short_url = custom_alias
            collides = await self._collision_check(short_url)
            if collides:
                raise ConflictException(f"Custom alias {short_url} is not available.")
            await self.create(
            {"user_id": user_id, "original_url": original_url, "short_url": short_url, **kwargs}
        )
            task = populate_preview.delay(short_url, original_url)
        else:
            short_url = await self._generate_short_url(original_url)
            await self.create(
                {"user_id": user_id, "original_url": original_url, "short_url": short_url, **kwargs}
            )
            task = populate_preview.delay(short_url, original_url)
        return short_url

    async def _scout_url_info(self, original_url: str) -> dict[str, Any]:
        preview = link_preview(original_url)
        return {"title": preview.title, "description": preview.description, "thumbnail": preview.image}

    async def _generate_short_url(self, original_url: str) -> str:
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        short_url = hash_url(original_url + salt)
        collides = await self._collision_check(short_url)
        if collides:
            log_this(f"Collision detected for {short_url}. Generating new hash.")
            short_url = await self._generate_short_url(original_url)
            return short_url
        else:
            return short_url

    async def _collision_check(self, short_url: str) -> bool:
        log_this(f"Checking for collision with {short_url}")
        return (
            await self._db_conn.get_collection(self._collection).find_one({"short_url": short_url})
            is not None
        )


_ANALYTICS_AGGREGATE = [{"$group": {"_id": "$short_url", "count": {"$sum": 1}}}]
url_handler = UrlHandler(db)