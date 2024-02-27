from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import ORJSONResponse


from app.core.dependencies import current_user_dep, url_handler, analytic_engine

router = APIRouter(default_response_class=ORJSONResponse, tags=["analytics"])

@router.get("/{short_link}")
async def get_full_analytics(short_link: str, handler: analytic_engine):
    res = await handler.get_full_analytics_data(short_link)
    return res


