from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from app.routers.limiter import limiter
from app.core.dependencies import AnalyticEngine

router = APIRouter(default_response_class=ORJSONResponse, tags=["analytics"])


@router.get("/{short_link}")
async def get_full_analytics(short_link: str, handler: AnalyticEngine):
    res = await handler.get_full_analytics_data(short_link)
    return res


@router.get("/{short_link}/granule")
async def get_specific_analytics(
    short_link: str, handler: AnalyticEngine, overview: bool, timeline: bool, location: bool, referrer: bool
):
    res = await handler.get_specific_analytics_data(short_link, overview, timeline, location, referrer)
    return res
