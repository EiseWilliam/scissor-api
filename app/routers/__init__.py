from fastapi import APIRouter, Depends
from app.routers import auth, url, user

all_router = APIRouter()
all_router.include_router(auth.router, prefix="/auth")
all_router.include_router(user.router, prefix="/user")
all_router.include_router(url.router, prefix="/link")
