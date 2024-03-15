from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates
from app.core.exceptions import URLNotFoundException
from app.main import app
from fastapi import Request
from slowapi.errors import RateLimitExceeded

from app.core.exceptions import URLNotFoundException
from app.main import app


templates = Jinja2Templates(directory="app/templates")

# @app.exception_handler(RateLimitExceeded)
# async def slowapi_rate_limiter_handler(request, exc):
# return _rate_limit_exceeded_handler(request, exc)

# @app.exception_handler(URLNotFoundException)
# async def url_not_found_handler(request, exc):
#     return URLNotFoundException.handler(request)


@app.exception_handler(URLNotFoundException)
async def url_not_exception_handler(request: Request, exc: URLNotFoundException):
    return templates.TemplateResponse(
        "404.jinja", {"request": request}, status_code=404
    )


@app.exception_handler(RateLimitExceeded)
async def slowapi_rate_limiter_handler(request: Request, exc: RateLimitExceeded):
    return ORJSONResponse(
        {
            "error": "Too many requests, slow down",
            "detail": f"You have exceeded the number of requests allowed in a given amount of time; {exc.detail}. Please try again later.",
        },
        status_code=429,
    )
