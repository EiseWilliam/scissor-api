from datetime import UTC, datetime
from typing import Literal
from fastapi.templating import Jinja2Templates

from app.core.dependencies import AnalyticEngine, CurrentUser, QRMaker, UrlHandler
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

router = APIRouter(default_response_class=ORJSONResponse, tags=["QR"])


@router.get("download/{short_url}")
async def download_qr(
    short_url: str,
    format: Literal["jpg", "svg", "png"],
    qr_handler: QRMaker,
    request: Request,
):
    return await qr_handler.download_qr(short_url, format, request)

@router.get("qrs")
async def get_user_qrs(qr_handler: QRMaker, user: CurrentUser):
    return await qr_handler.get_user_qrs(user.id)