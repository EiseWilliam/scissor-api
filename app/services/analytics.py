import requests
from fastapi import Request
from redis import Redis
from user_agents import parse

from app.core.exceptions import NotFoundException
from app.core.logging import log_this
from app.schemas.url import UrlAnalyticsResponse
from app.services.pipelines import (
    gen_countries_and_cities_pipeline,
    gen_overview_pipeline,
    gen_referrer_pipeline,
    gen_summary_pipeline,
)



class AnalyticsEngine:
    def __init__(self, db_conn):
        self._db_conn = db_conn
        self.redis: Redis = Redis()
        
    async def get_summary_stats(self, short_url:str):
        return await self._db_conn.get_collection("analytics").aggregate(gen_summary_pipeline(short_url)).to_list(None)    
    
    async def get_overview_stats(self, short_url: str):
        return (await self._db_conn.get_collection("analytics").aggregate(gen_overview_pipeline(short_url)).to_list(None))[0]
    
    async def get_referral_stats(self, short_url: str):
        data = await self._db_conn.get_collection("analytics").aggregate(gen_referrer_pipeline(short_url)).to_list(None)
        referrers = {}
        for referrer in data:
            referrers[referrer["referral"]] = referrer["amount"]
        if None in referrers:
            referrers["direct"] = referrers.pop(None)
        return referrers
    
    async def get_location_stats(self, short_url: str):
        data = await self._db_conn.get_collection("analytics").aggregate(gen_countries_and_cities_pipeline(short_url)).to_list(None)
        countries = {}
        cities = {}
        for country in data[0]["countries"]:
            country_name = country["country"]
            city_count = country["cities"][0]["count"]
            countries[country_name] = countries.get(country_name, 0) + city_count

            for city in country["cities"]:
                city_name = city["city"]
                city_count = city["count"]
                cities[city_name] = cities.get(city_name, 0) + city_count
        return {
            "countries": countries,
            "cities": cities
        }
       
                                                          
    async def get_full_analytics_data(self, short_url: str):
        # timeline_data = await self.get_timeline()
        return {
            # "summary": await self.get_summary_stats(short_url),
            "overview": await self.get_overview_stats(short_url),
            "referrers": await self.get_referral_stats(short_url),
            "location": await self.get_location_stats(short_url)
        }

    async def normalize_full_analytics_data(self):
        timeline_data = ...
        overview_data = ...
        countries_data = ...
        device_data = ...

    async def get_url_analytics(self, short_url: str) -> UrlAnalyticsResponse:
        result = await self._db_conn.get_collection("analytics").find({"short_url": short_url}).to_list(None)
        if result:
            return UrlAnalyticsResponse(
                activities=result,
                total_clicks=len(result),
                last_clicked=result[-1].get("timestamp") if result else None,
            )
        raise NotFoundException(f"No analytics found for {short_url}")

    def update_clicks(self, click_data: dict):
        self.redis.incr(click_data["short_url"])
        self.redis.hmset(click_data["short_url"], click_data)

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
        self, short_url: str, original_url: str, request: Request, timestamp: str, **kwargs
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
        self.redis.hincrby(f"analytic:{short_url}", "clicks", 1)
        self.redis.hincrby(f"analytic:{short_url}", "total_activites", 1)
        self.redis.hset(f"analytic:{short_url}", "last_clicked", timestamp)

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

    async def get_analytic(self, short_url: str):
        return self.redis.hgetall(f"analytic:{short_url}")

    async def get_full_analytics(self):
        return self.redis.keys("analytic:*")
