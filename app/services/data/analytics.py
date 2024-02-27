from datetime import UTC, datetime
from typing import Literal


import orjson
import requests
from fastapi import Request
from redis.asyncio import Redis
from user_agents import parse
from app.core.config.settings import settings

from app.core.exceptions import NotFoundException
from app.core.logging import log_this
from app.schemas.url import UrlAnalyticsResponse
from app.services.data.pipelines import (
    gen_countries_and_cities_pipeline,
    gen_overview_pipeline,
    gen_referrer_pipeline,
    gen_timeline_pipeline,
)
from app.services.data.refine import process_location, process_timeline


AGGREGATION_INTERVAL = settings.AGGREGATION_INTERVAL

class AnalyticsEngine:
    def __init__(self, db_conn):
        self._db_conn = db_conn
        self.redis: Redis = Redis()

    async def _get_overview_stats(self, short_url: str, start_from: datetime | str | None = None):
        return (
            await self._db_conn.get_collection("analytics")
            .aggregate(gen_overview_pipeline(short_url))
            .to_list(None)
        )[0]

    async def _get_timeline_stats(
        self, short_url: str, interval: Literal["h", "d"] = "d", start_from: datetime | str | None = None
    ):
        data = (
            await self._db_conn.get_collection("analytics")
            .aggregate(gen_timeline_pipeline(short_url))
            .to_list(None)
        )
        return process_timeline(data, interval)

    async def _get_referral_stats(self, short_url: str, start_from: datetime | str | None = None):
        data = (
            await self._db_conn.get_collection("analytics")
            .aggregate(gen_referrer_pipeline(short_url))
            .to_list(None)
        )
        referrers = {}
        for referrer in data:
            referrers[referrer["referral"]] = referrer["amount"]
        if None in referrers:
            referrers["direct"] = referrers.pop(None)
        return referrers

    async def _get_location_stats(self, short_url: str, start_from: datetime | str | None = None):
        data = (
            await self._db_conn.get_collection("analytics")
            .aggregate(gen_countries_and_cities_pipeline(short_url))
            .to_list(None)
        )
        countries, cities = process_location(data)
        return {"countries": countries, "cities": cities}

    async def _validate_cache_aggr(self, short_url: str) -> bool:
        result = await self.redis.hmget(f"analytics:{short_url}", "last_updated", "last_activity")  # type: ignore
        last_updated, last_activity = result
        if last_updated and last_activity:
            last_updated, last_activity = last_updated.decode("utf-8"), last_activity.decode("utf-8")
            last_updated = datetime.fromisoformat(last_updated)
            last_activity = datetime.fromisoformat(last_activity)
            if last_activity > last_updated:
                log_this(f"Cache is stale, last updated: {last_updated}, last activity: {last_activity}")
                return False
            if (datetime.now(UTC) - last_updated).seconds > AGGREGATION_INTERVAL * 60:
                log_this(f"Cache is stale, last updated: {last_updated}, last activity: {last_activity}")
                return False
            return True
        return False

    async def get_full_analytics_data(self, short_url: str):
        if not await self._validate_cache_aggr(short_url):
            log_this("Cache miss, aggregating from analytics data")
            await self.save_aggr_to_redis(short_url)
        return await self.get_aggr_from_redis(short_url)

    async def get_aggr_from_redis(self, short_url: str):
        result = await self.redis.hgetall(f"analytics:{short_url}")  # type: ignore
        result = {k.decode("utf-8"): v.decode("utf-8") for k, v in result.items()}
        analytics_data = {
            "timeline": orjson.loads(result["timeline"]),
            "overview": orjson.loads(result["overview"]),
            "referrers": orjson.loads(result["referrers"]),
            "location": orjson.loads(result["location"]),
        }
        return analytics_data

    async def save_aggr_to_redis(self, short_url: str):
        timeline = await self._get_timeline_stats(short_url)
        overview = await self._get_overview_stats(short_url)
        referrers = await self._get_referral_stats(short_url)
        location = await self._get_location_stats(short_url)
        await self.redis.hmset(
            f"analytics:{short_url}",
            {
                "last_updated": datetime.now(UTC).isoformat(),
                "timeline": orjson.dumps(timeline),
                "overview": orjson.dumps(overview),
                "referrers": orjson.dumps(referrers),
                "location": orjson.dumps(location),
            },
        )  # type: ignore

    async def get_url_analytics(self, short_url: str) -> UrlAnalyticsResponse:
        result = await self._db_conn.get_collection("analytics").find({"short_url": short_url}).to_list(None)
        if result:
            return UrlAnalyticsResponse(
                activities=result,
                total_clicks=len(result),
                last_clicked=result[-1].get("timestamp") if result else None,
            )
        raise NotFoundException(f"No analytics found for {short_url}")

    async def cache_url_analytics(self, short_url: str) -> None:
        result = await self.get_url_analytics(short_url)
        await self.redis.set(f"analytics:{short_url}", result.json())

    async def _get_location(self, ip_address: str = "105.112.183.107") -> dict[str, str]:
        response = requests.get(f"http://ipinfo.io/{ip_address}/json")
        data = response.json()
        location = {
            # "ip": data["ip"],
            "city": data["city"],
            "region": data["region"],
            "country": data["country"],
            # "loc": data["loc"],
            # "org": data["org"],
        }
        return location

    async def track_click(
        self, short_url: str, original_url: str, request: Request, timestamp: datetime, **kwargs
    ) -> None:
        referer = request.headers.get("Referer")
        user_agent_string = request.headers.get("User-Agent")
        user_agent = parse(user_agent_string)
        os = user_agent.os.family
        device = user_agent.device.family
        ip_address = request.client.host if request.client else None
        location = await self._get_location()  # TODO: get location from real ip address

        log_this(f"Tracking click for {short_url}, Referer: {referer} Timestamp: {timestamp}")
        # update cache
        await self.redis.hincrby(f"analytics:{short_url}", "clicks", 1) # type: ignore
        await self.redis.hincrby(f"analytics:{short_url}", "total_activites", 1) # type: ignore
        await self.redis.hset(f"analytics:{short_url}", "last_activity", timestamp.isoformat()) # type: ignore

        # update db
        await self._db_conn.get_collection("analytics").insert_one(
            {
                "short_url": short_url,
                "type": "click",
                "referer": referer,
                "timestamp": timestamp,
                "ip_address": ip_address,
                "os": os,
                "device": device,
                "original_url": original_url,
                **location,
                **kwargs,
            }
        )

    async def track_scan(self, short_url: str, original_url: str, request: Request, timestamp: str, **kwargs):
        pass

