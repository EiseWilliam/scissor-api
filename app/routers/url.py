from datetime import UTC, datetime
from typing import Annotated, Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.routing import APIRoute
from pydantic import HttpUrl

from app.core.dependencies import AnalyticEngine, CurrentUser, UrlHandler
from app.core.logging import log_this
from app.core.responses import direct_response
from app.core.utils.analytics import extract_from_request
from app.schemas.qr import QROptions
from app.schemas.url import ShortenUrl, UpdateUrl, UrlClicks
from app.services.qr import build_qr_code
from app.services.tasks import track_activity

router = APIRouter(default_response_class=ORJSONResponse, tags=["url"])
qrrouter = APIRouter(default_response_class=ORJSONResponse, tags=["QR"])


@qrrouter.post("/qr_code")
async def generate_qr_code(
    url: str,
    options: QROptions,
    request: Request,
    handler: UrlHandler,
    user: CurrentUser,
    is_short_url: bool = True,
):
    """
    Generate a QR code for the given URL.

    Args:
        url (str): The URL to generate the QR code for.
        options (QROptions): The options for customizing the QR code.
        requests (Request): The request object.
        handler (UrlHandler): The URL handler object.
        user (CurrentUser): The current user object.
        is_short_url (bool, optional): Whether to URL is already shortened. Defaults to True.

    Returns:
        qr (QRCode): The generated QR code.
    """
    if not is_short_url:
        url = await handler.shorten_url(user.id, url, has_qr=True)
    host_url = request.base_url
    full_url = f"{host_url}{url}?ref=qr"
    qr = build_qr_code(full_url, url, **options.model_dump(exclude_unset=True))
    return qr


@router.get("/verify_custom")
async def check_custom_alias_availability(
    alias: str,
    handler: UrlHandler,
):
    return await handler.custom_alias_is_available(alias)


@qrrouter.post("/quick_qr")
async def create_qr_code(
    url: str,
    options: QROptions,
    request: Request,
    handler: UrlHandler,
    is_short_url: bool = False,
):
    if not is_short_url:
        url = await handler.shorten_url("annonymous", url, has_qr=True)
    host_url = request.base_url
    full_url = f"{host_url}{url}?ref=qr"
    qr = build_qr_code(full_url, url, **options.model_dump(exclude_unset=True))
    return qr


@router.post("/shorten", summary="Create a new short link.")
async def create_new_short_link(data: ShortenUrl, user: CurrentUser, handler: UrlHandler, request: Request):
    url = str(data.url)
    short_link = await handler.shorten_url(user.id, url, data.custom_alias)
    host_url = request.base_url
    if str(host_url).startswith("http://"):
        full_url = f"{host_url}{short_link}".removeprefix("http://")
        return full_url
    full_url = f"{host_url}{short_link}".removeprefix("https://")
    return full_url


@router.post("/quick_shorten")
async def annonymous_create_short_link(url: HttpUrl, handler: UrlHandler, request: Request):
    url_str = str(url)
    short_link = await handler.shorten_url("annonymous", url_str)
    host_url = request.base_url
    if str(host_url).startswith("http://"):
        full_url = f"{host_url}{short_link}".removeprefix("http://")
        return full_url
    full_url = f"{host_url}{short_link}".removeprefix("https://")
    return full_url


@router.get("/my_urls")
async def get_user_urls(user: CurrentUser, handler: UrlHandler):
    urls = await handler.get_user_urls(user.id)
    return direct_response(urls)


@router.patch("/my_urls/{short_url}")
async def update_url(short_url, updates: UpdateUrl, user: CurrentUser, handler: UrlHandler):
    if await handler.update_url(short_url, user.id, **updates.model_dump()):
        return ORJSONResponse(None, status_code=status.HTTP_204_NO_CONTENT)
    
@router.delete("/my_urls/{short_url}")
async def delete_url(short_url, user: CurrentUser, handler: UrlHandler):
    if await handler.delete_url(short_url, user.id):
        return ORJSONResponse(None, status_code=status.HTTP_204_NO_CONTENT)


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
async def get_url_clicks_for_user(user: CurrentUser, analytic: AnalyticEngine, handler: UrlHandler):
    # res = await handler.get_url_analytics(short_link)
    res = await handler.get_user_recent_urls(user.id)
    data = await analytic.get_url_clicks([urldata["short_url"] for urldata in res["urls"]])
    return data

root_router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@root_router.get("/+{short_link}")
async def show_url_info(short_link: str, handler: UrlHandler, analytic: AnalyticEngine):
    url_info = await handler.get_url_details(short_link)
    return url_info


@root_router.get("/{short_link}")
async def forward_to_target_url(
    short_link: str,
    request: Request,
    handler: UrlHandler,
    ref: str | None = None
):
    true_url = await handler.get_original_url(short_link)
    if true_url:
        referrer, user_agent, ip_address = extract_from_request(request)
        # background_tasks.add_task(
        #     analytics.track_click, short_link, true_url, user_agent, ip_address, referrer, datetime.now(UTC)
        # )
        track_activity.delay(short_link, ref, true_url, user_agent, ip_address, referrer, datetime.now(UTC))
        return RedirectResponse(true_url)
    else:
        log_this(f"URL not found for {short_link}")
        return RedirectResponse("/404/")


redirect_route = APIRoute(
    "/{short_link}",
    forward_to_target_url,
    methods=["GET"],
    response_class=RedirectResponse,
    name="redirect",
    # route_class_override = re.compile(r"/[a-zA-Z0-9]{7}")
)

details_route = APIRoute(
    "/+{short_link}",
    show_url_info,
    methods=["GET"],
    name="details",
)
