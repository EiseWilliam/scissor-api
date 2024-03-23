from app.routers import analytics, auth, url, user

from app.routers import analytics, auth, url, user, qr
from fastapi import APIRouter


all_router = APIRouter()
all_router.include_router(auth.router, prefix="/auth")
all_router.include_router(user.router, prefix="/user")
all_router.include_router(url.router, prefix="/url")
all_router.include_router(qr.router, prefix="/url")
all_router.include_router(analytics.router, prefix="/analytics")
