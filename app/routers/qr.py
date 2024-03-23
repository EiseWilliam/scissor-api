from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

from app.core.dependencies import CurrentUser, QRMaker, UrlHandler
from app.core.responses import direct_response
from app.routers.limiter import limiter
from app.schemas.qr import QROptions
from app.services.qr import build_qr_code

router = APIRouter(default_response_class=ORJSONResponse, tags=["QR"])


@router.post("/quick_qr")
@limiter.limit("5/minute")
async def create_qr_code(
    url: str,
    options: QROptions,
    request: Request,
    handler: UrlHandler,
    is_short_url: bool = False,
):
    if not is_short_url:
        url = await handler.shorten_url("anonymous", url, has_qr=True)
    host_url = request.base_url
    full_url = f"{host_url}{url}?ref=qr"
    qr = build_qr_code(full_url, url, **options.model_dump(exclude_unset=True))
    return qr


@router.post("/generate")
@limiter.limit("5/minute")
async def generate_qr_code(
    url: str,
    options: QROptions,
    request: Request,
    handler: QRMaker,
    user: CurrentUser,
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
    # if not is_short_url:
    #     url = await handler.shorten_url(user.id, url, has_qr=True)
    # host_url = request.base_url
    # full_url = f"{host_url}{url}?ref=qr"
    # qr = build_qr_code(full_url, url, **options.model_dump(exclude_unset=True))
    # return qr
    qr = await handler.make_qr_for_short_url(url, options.color, request)
    return qr


@router.get("/download/{short_url}")
async def download_qr(
    short_url: str,
    format: Literal["jpg", "svg", "png"],
    qr_handler: QRMaker,
    request: Request,
):
    return await qr_handler.download_qr(short_url, format, request)


@router.get("/my_qrs")
async def get_user_qrs(qr_handler: QRMaker, user: CurrentUser):
    return direct_response(await qr_handler.get_user_qrs(user.id))


