from datetime import UTC, datetime
from typing import Literal

import orjson
import requests
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis
from user_agents import parse

from app.core.config.settings import settings
from app.core.exceptions import NotFoundException
from app.core.logging import log_this
from app.db.database import db
from app.schemas.url import UrlAnalyticsResponse
from app.services.data.pipelines import (
    gen_countries_and_cities_pipeline,
    gen_overview_pipeline,
    gen_referrer_pipeline,
    gen_timeline_pipeline,
)
from app.services.data.refine import process_location, process_timeline

AGGREGATION_INTERVAL = settings.AGGREGATION_INTERVAL
REDIS_URL = settings.REDIS_URL

class AnalyticsEngine:
    def __init__(self, db_conn: AsyncIOMotorDatabase):
        self._db_conn = db_conn
        self.redis: Redis = Redis(host=REDIS_URL, decode_responses=True)

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
        if None in referrers or "" in referrers:
            referrers["direct"] += referrers.pop(None, 0)
            referrers["direct"] += referrers.pop("", 0)
        return referrers

    async def _get_location_stats(self, short_url: str, start_from: datetime | str | None = None):
        data = (
            await self._db_conn.get_collection("analytics")
            .aggregate(gen_countries_and_cities_pipeline(short_url))
            .to_list(None)
        )
        country_codes, countries, cities = process_location(data)
        return {"countries": countries, "cities": cities, "country_codes": country_codes}

    async def _validate_cache_aggr(self, short_url: str) -> bool:
        result = await self.redis.hmget(f"analytics:{short_url}", "last_updated", "last_activity")  # type: ignore
        last_updated, last_activity = result
        if last_updated and last_activity:
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

    async def get_specific_analytics_data(self, short_url: str):
        pass

    async def get_quick_overview(self, short_url: str):
        res = await self.redis.hget(f"analytics:{short_url}", "clicks")  # type: ignore
        if res:
            return orjson.loads(res)
        else:
            # TODO
            pass

    async def get_url_clicks(self, short_url: list[str]):
        tasks = [await self.redis.hget(f"analytics:{short}", "clicks") for short in short_url]  # type: ignore
        return {k: int(v) if v is not None else 0 for k, v in zip(short_url, tasks)}
    
    async def get_aggr_from_redis(self, short_url: str):
        result = await self.redis.hgetall(f"analytics:{short_url}")  # type: ignore
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
        # response = requests.get(f"http://ipinfo.io/{ip_address}/json")
        response = {
            "ip": "105.112.73.42",
            "rir": "AFRINIC",
            "is_bogon": False,
            "is_mobile": False,
            "is_crawler": False,
            "is_datacenter": False,
            "is_tor": False,
            "is_proxy": False,
            "is_vpn": True,
            "is_abuser": True,
            "company": {
                "name": "Airtel Networks Limited",
                "abuser_score": "0.0008 (Low)",
                "domain": "www.airtel.com.ng",
                "type": "isp",
                "network": "105.112.0.0 - 105.127.255.255",
                "whois": "https://api.ipapi.is/?whois=105.112.0.0",
            },
            "asn": {
                "asn": 36873,
                "abuser_score": "0.0012 (Low)",
                "route": "105.112.73.0/24",
                "descr": "VNL1-AS, NG",
                "country": "ng",
                "active": True,
                "org": "Airtel Networks Limited",
                "domain": "www.airtel.com.ng",
                "type": "isp",
                "rir": "AFRINIC",
                "whois": "https://api.ipapi.is/?whois=AS36873",
            },
            "location": {
                "continent": "AF",
                "country": "USA",
                "country_code": "US",
                "state": "Manhanttan",
                "city": "New York",
                "latitude": 6.453,
                "longitude": 3.396,
                "zip": "102103",
                "timezone": "Africa/Lagos",
                "local_time": "2024-03-03T14:58:59+01:00",
                "local_time_unix": 1709474339,
                "is_dst": False,
            },
            "elapsed_ms": 0.65,
        }
        # response = requests.get(f"http://ip-api.com/json/{ip_address}")
        # data = response.json()
        data = response
        location_data =  data["location"]
        company_data = data["company"]
        location = {
            # "ip": data["ip"],
            "city": location_data["city"],
            "continent": location_data["continent"],
            "region": location_data["state"],
            "country_code": location_data["country_code"],
            "country": location_data["country"],
            "isp": company_data["name"],
            # "loc": data["loc"],
            # "org": data["org"],
        }
        return location

    async def track_click(
        self,
        short_url: str,
        original_url: str,
        user_agent_string: str,
        ip_address: str,
        referer: str,
        timestamp: datetime,
        **kwargs,
    ) -> bool:

        user_agent = parse(user_agent_string)
        device = user_agent.device.family
        os = user_agent.os.family
        location = await self._get_location()  # TODO: get location from real ip address

        log_this(f"Tracking click for {short_url}, Referer: {referer} Timestamp: {timestamp}")
        # update cache
        await self.redis.hincrby(f"analytics:{short_url}", "clicks", 1)  # type: ignore
        await self.redis.hincrby(f"analytics:{short_url}", "total_activites", 1)  # type: ignore
        await self.redis.hset(f"analytics:{short_url}", "last_activity", timestamp.isoformat())  # type: ignore

        # update db
        res = await self._db_conn.get_collection("analytics").insert_one(
            {
                "short_url": short_url,
                "type": "click",
                "referer": referer if referer else "direct",
                "timestamp": timestamp,
                "ip_address": ip_address,
                "os": os,
                "device": device,
                "original_url": original_url,
                **location,
                **kwargs,
            }
        )
        return res.acknowledged

    async def track_scan(
        self,
        short_url: str,
        original_url: str,
        user_agent_string: str,
        ip_address: str,
        referer: str,
        timestamp: datetime,
        **kwargs,
    ) -> bool:

        user_agent = parse(user_agent_string)
        device = user_agent.device.family
        os = user_agent.os.family
        location = await self._get_location()  # TODO: get location from real ip address

        log_this(f"Tracking scan for {short_url}, Referer: {referer} Timestamp: {timestamp}")
        # update cache
        await self.redis.hincrby(f"analytics:{short_url}", "clicks", 1)  # type: ignore
        await self.redis.hincrby(f"analytics:{short_url}", "total_activites", 1)  # type: ignore
        await self.redis.hset(f"analytics:{short_url}", "last_activity", timestamp.isoformat())  # type: ignore

        # update db
        res = await self._db_conn.get_collection("analytics").insert_one(
            {
                "short_url": short_url,
                "type": "scan",
                "referer": referer if referer else "direct",
                "timestamp": timestamp,
                "ip_address": ip_address,
                "os": os,
                "device": device,
                "original_url": original_url,
                **location,
                **kwargs,
            }
        )
        return res.acknowledged


analytics_processor = AnalyticsEngine(db_conn=db)
