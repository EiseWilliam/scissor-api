import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers.url import redirect_route, details_route
from app.core.dependencies import db as db_conn
from app.routers import all_router, url

app = FastAPI(
    title="Scissors API",
    version="0.1.0",
    description="API for Scissors",
    default_response_class=ORJSONResponse,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print(f"body : {await request.body()}")
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(all_router, prefix="/api")


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

# app.include_router(redirect_route)

app.include_router(url.root_router)