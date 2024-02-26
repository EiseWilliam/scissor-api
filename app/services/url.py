from typing import Any

from bson import ObjectId
from linkpreview import link_preview
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ConflictException, NotFoundException
from app.core.logging import log_this
from app.core.utils.url import hash_url
from app.schemas.url import ListUrl, UrlAnalyticsResponse
from app.services.base_crud import BaseCRUD


class UrlHandler(BaseCRUD):
    def __init__(self, db_conn: AsyncIOMotorDatabase):  # type: ignore
        super().__init__(db_conn, "urls")


    async def get_url_analytics(self, short_url: str) -> UrlAnalyticsResponse:
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

    async def get_original_url(self, short_url: str):
        log_this(f"Getting original URL for {short_url}")
        doc = await self._db_conn.get_collection(self._collection).find_one({"short_url": short_url})
        if doc:
            return doc["original_url"]
        log_this(f"No original URL found for {short_url}")

    async def shorten_url(self, user_id: str | ObjectId, original_url: str, custom_alias: str | None = None):
        url_data = await self._scout_url_info(original_url)
        if custom_alias:
            short_url = custom_alias
            collides = await self.collision_check(short_url)
            if collides:
                raise ConflictException(f"Custom alias {short_url} is not available.")
            return short_url
        short_url = await self._generate_short_url(original_url)
        await self.create(
            {"user_id": user_id, "original_url": original_url, "short_url": short_url, **url_data}
        )
        return short_url

    async def _scout_url_info(self, original_url: str) -> dict[str, Any]:
        preview = link_preview(original_url)
        return {"title": preview.title, "description": preview.description, "thumbnail": preview.image}

    async def _generate_short_url(self, original_url: str) -> str:
        short_url = hash_url(original_url)
        collides = await self.collision_check(short_url)
        if collides:
            log_this(f"Collision detected for {short_url}. Generating new hash.")
            short_url = await self._generate_short_url(short_url)
            return short_url
        else:
            return short_url

    async def collision_check(self, short_url: str) -> bool:
        log_this(f"Checking for collision with {short_url}")
        return (
            await self._db_conn.get_collection(self._collection).find_one({"short_url": short_url})
            is not None
        )


_ANALYTICS_AGGREGATE = [{"$group": {"_id": "$short_url", "count": {"$sum": 1}}}]
