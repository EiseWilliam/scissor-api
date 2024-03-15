import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config.settings import settings
from app.core.exceptions import NotFoundException, URLNotFoundException
from app.routers.url import redirect_route, details_route
from app.core.dependencies import db as db_conn
from app.routers import all_router, url
from app.routers.limiter import limiter



app = FastAPI(
    title="Scissors API",
    version="0.1.0",
    description="API for Scissors",
    default_response_class=ORJSONResponse,
    debug=settings.DEBUG,
)
app.state.limiter = limiter
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
@limiter.limit("5/minute")
async def welcome(request: Request):
    return {"message": "Welcome to Scissors API"}

@app.get("/test")
async def test(db: db_conn):
    info = await db.list_collection_names()
    return info

app.include_router(all_router, prefix="/api")
app.include_router(url.root_router)