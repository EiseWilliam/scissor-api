from datetime import UTC, datetime
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import ORJSONResponse, RedirectResponse

from app.core.dependencies import current_user_dep, url_handler, analytic_engine as ae
from app.core.logging import log_this
from app.core.responses import direct_response
from app.schemas.url import ShortenUrl

# from app.services.user import user_handler
router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@router.post("/shorten", summary="Create a new short link.")
async def create_new_short_link(
    data: Annotated[ShortenUrl, Depends()], user: current_user_dep, handler: url_handler
):
    short_link = await handler.shorten_url(user.id, data.url, data.custom_alias)
    return short_link

@router.get("/my_urls")
async def get_user_urls(user: current_user_dep, handler: url_handler):
    urls = await handler.get_user_urls(user.id)
    return urls

@router.get("/{short_link}/stats",)# response_model=UrlAnalyticsResponse)
async def get_url_analytics(short_link: str, handler: ae):
    # res = await handler.get_url_analytics(short_link)
    res = await handler.get_url_analytics(short_link)
    # return res
    return direct_response(res)


root_router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@root_router.get("/+{short_link}")
async def show_url_info(short_link: str, handler: url_handler):
    url_info = await handler.get_url_quickinfo(short_link)
    return url_info

@root_router.get("/{short_link}")
async def forward_to_target_url(
    short_link: str, request: Request, handler: url_handler, analytics: ae, background_tasks: BackgroundTasks
):
    true_url = await handler.get_original_url(short_link)
    if true_url:
        background_tasks.add_task(
            analytics.track_click, short_link, true_url, request, datetime.now(UTC)
        )
        return RedirectResponse(true_url)
    else:
        log_this(f"URL not found for {short_link}")
        return RedirectResponse("/404/")
