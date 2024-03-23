from datetime import UTC, datetime
from urllib import request

from fastapi.templating import Jinja2Templates

from app.core.dependencies import AnalyticEngine, CurrentUser, UrlHandler
from app.core.logging import log_this
from app.core.responses import direct_response
from app.core.utils.analytics import extract_from_request
from app.routers.limiter import limiter
from app.schemas.qr import QROptions
from app.schemas.url import ShortenUrl, UpdateUrl, UrlClicks
from app.services.qr import build_qr_code
from app.services.tasks import track_activity
from fastapi import APIRouter, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.routing import APIRoute
from pydantic import HttpUrl

router = APIRouter(default_response_class=ORJSONResponse, tags=["url"])

templates = Jinja2Templates(directory="app/templates")



@router.get("/verify_custom")
@limiter.limit("20/minute")
async def check_custom_alias_availability(
    alias: str,
    handler: UrlHandler,
    user: CurrentUser,
    request: Request
):
    return await handler.custom_alias_is_available(alias)




@router.post("/shorten", summary="Create a new short link.")
@limiter.limit("5/minute")
async def create_new_short_link(
    data: ShortenUrl, user: CurrentUser, handler: UrlHandler, request: Request
):
    url = str(data.url)
    short_link = await handler.shorten_url(user.id, url, data.custom_alias)
    host_url = request.base_url
    if str(host_url).startswith("http://"):
        return f"{host_url}{short_link}".removeprefix("http://")
    return f"{host_url}{short_link}".removeprefix("https://")


@router.post("/quick_shorten")
async def annonymous_create_short_link(
    url: HttpUrl, handler: UrlHandler, request: Request
):
    url_str = str(url)
    short_link = await handler.shorten_url("annonymous", url_str)
    host_url = request.base_url
    if str(host_url).startswith("http://"):
        full_url = f"{host_url}{short_link}".removeprefix("http://")
        return full_url
    full_url = f"{host_url}{short_link}".removeprefix("https://")
    return full_url


@router.get("/my_urls")
async def get_user_urls(user: CurrentUser, handler: UrlHandler, request: Request):
    urls = await handler.get_user_urls(user.id)
    return direct_response(urls)



@router.get("/my_urls/{short_url}")
async def get_url(short_url, user: CurrentUser, handler: UrlHandler):
    url_info = await handler.get_url_details(short_url)
    return url_info

@router.patch("/my_urls/{short_url}")
async def update_url(
    short_url, updates: UpdateUrl, user: CurrentUser, handler: UrlHandler
):
    if await handler.update_url(short_url, user.id, **updates.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)):
        return ORJSONResponse(None, status_code=200)


@router.delete("/my_urls/{short_url}")
async def delete_url(short_url, user: CurrentUser, handler: UrlHandler):
    if await handler.delete_url(short_url, user.id):
        return ORJSONResponse(None, status_code=200)


@router.post(
    "/stats",
)  # response_model=UrlAnalyticsResponse)
async def get_url_clicks(short_link: UrlClicks, handler: AnalyticEngine):
    # res = await handler.get_url_analytics(short_link)
    res = await handler.get_url_clicks(short_link.short_urls)
    return res
    # return direct_response(res)


@router.get(
    "/stats",
)  # response_model=UrlAnalyticsResponse)
async def get_url_clicks_for_user(
    user: CurrentUser, analytic: AnalyticEngine, handler: UrlHandler
):
    res = await handler.get_user_recent_urls(user.id)
    data = await analytic.get_url_clicks(
        [urldata["short_url"] for urldata in res["urls"]]
    )
    return data


root_router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@root_router.get("/+{short_link}")
async def show_url_info(short_link: str, handler: UrlHandler, analytic: AnalyticEngine):
    url_info = await handler.get_url_details(short_link)
    return url_info


@root_router.get("/{short_link}")
async def forward_to_target_url(
    short_link: str, request: Request, handler: UrlHandler, ref: str | None = None
):
    true_url = await handler.get_original_url(short_link)
 
    referrer, user_agent, ip_address = extract_from_request(request)
    track_activity.delay(
        short_link,
        ref,
        true_url,
        user_agent,
        ip_address,
        referrer,
        datetime.now(UTC),
    )
    return RedirectResponse(true_url)


redirect_route = APIRoute(
    "/{short_link}",
    forward_to_target_url,
    methods=["GET"],
    response_class=RedirectResponse,
    name="redirect",
)

details_route = APIRoute(
    "/+{short_link}",
    show_url_info,
    methods=["GET"],
    name="details",
)
