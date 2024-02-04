from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse, RedirectResponse

from app.core.dependencies import current_user_dep, url_handler

# from app.services.user import user_handler
router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@router.post("/shorten", summary="Create a new short link.")
async def create_new_short_link(original_url: str, user: current_user_dep, handler: url_handler):
    short_link = await handler.shorten_url(user.id, original_url)
    return short_link


redirect_router = APIRouter(default_response_class=ORJSONResponse, tags=["link"])


@redirect_router.get("/{short_link}")
async def forward_to_target_url(short_link: str, request: Request, handler: url_handler):
    true_url = await handler.get_original_url(short_link)
    if true_url:
        return RedirectResponse(true_url)
    else:
        return RedirectResponse("/404/")
