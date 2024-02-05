from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.dependencies import db as db_conn
from app.routers import all_router, url

app = FastAPI(
    title="Scissors API",
    version="0.1.0",
    description="API for Scissors",
    default_response_class=ORJSONResponse,
)
app.include_router(all_router, prefix="/api")
app.include_router(url.redirect_router)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def welcome():
    return {"message": "Welcome to Scissors API"}

@app.get("/404/")
async def not_found(request: Request):
    return templates.TemplateResponse("404.jinja", {"request": request})

# test mongodb connection
@app.get("/test")
async def test(db: db_conn):
    info = await db.list_collection_names()
    return info
