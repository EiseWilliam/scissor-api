from fastapi import APIRouter, Depends
from app.routers import auth, url, user, analytics

all_router = APIRouter()
all_router.include_router(auth.router, prefix="/auth")
all_router.include_router(user.router, prefix="/user")
all_router.include_router(url.router, prefix="/url")
all_router.include_router(url.qrrouter, prefix="/url")
all_router.include_router(analytics.router, prefix="/analytics")
