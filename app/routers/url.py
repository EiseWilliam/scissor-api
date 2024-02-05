from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import ORJSONResponse, RedirectResponse

from app.core.dependencies import current_user_dep, url_handler
from app.core.logging import log_this
from app.core.responses import direct_response
from app.schemas.url import ShortenUrl, UrlAnalyticsResponse

# from app.services.user import user_handler
router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@router.post("/shorten", summary="Create a new short link.")
async def create_new_short_link(
    data: Annotated[ShortenUrl, Depends()], user: current_user_dep, handler: url_handler
):
    short_link = await handler.shorten_url(user.id, data.url, data.custom_alias)
    return short_link


@router.get("/analytics/{short_link}", response_model=UrlAnalyticsResponse)
async def get_url_analytics(short_link: str, handler: url_handler):
    res = await handler.get_url_analytics(short_link)
    return direct_response(res)


redirect_router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@redirect_router.get("/{short_link}")
async def forward_to_target_url(
    short_link: str, request: Request, handler: url_handler, background_tasks: BackgroundTasks
):
    true_url = await handler.get_original_url(short_link)
    if true_url:
        background_tasks.add_task(
            handler.track_click, short_link, true_url, request, datetime.now(UTC).isoformat()
        )
        return RedirectResponse(true_url)
    else:
        log_this(f"URL not found for {short_link}")
        return RedirectResponse("/404/")
