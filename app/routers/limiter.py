from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.settings import settings


STORAGE_URI = settings.CELERY_RESULT_BACKEND

limiter = Limiter(key_func=get_remote_address, default_limits=["3 per minute"], storage_uri=STORAGE_URI)