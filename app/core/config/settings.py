import os
from xxlimited import Str
from fastapi.datastructures import URL

from pydantic_settings import BaseSettings
from starlette.config import Config


root_dir = os.path.abspath(os.path.join(__file__, "..", "..", "..", "..")) 
env_path = os.path.join(root_dir, ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)
    HOST_URL: str | None = config("HOST_URL", default="localhost:8000")
    DEBUG: bool = config("DEBUG", default=True)
    
class CelerySettings(BaseSettings):
    CELERY_BROKER_URL: str = config("CELERY_BROKER_URL", default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = config("CELERY_RESULT_BACKEND", default="redis://redis:6379/0")

class AnalyticsSettings(BaseSettings):
    AGGREGATION_INTERVAL : int = config("AGGREGATION_INTERVAL", default=60) # in minutes

class ShortServiceSettings(BaseSettings):
    CACHE_MAP_URLS: bool = config("MAP_URLS", default=True)
    URL_LENGTH: int = config("URL_LENGTH", default=7)


class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY", default="secret")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class RedisSettings(BaseSettings):
    REDIS_URI: str = config("REDIS_URI", default="redis://redis:6379/0")
    REDIS_URL: str = config("REDIS_URL", default="redis://redis:6379/0")
    REDIS_HOST: str = config("REDIS_HOST", default="redis")
    REDIS_PORT: int = config("REDIS_PORT", default=6379)
    REDIS_USER: str | None = config("REDIS_USER", default=None)
    REDIS_PASS: str | None = config("REDIS_PASS", default=None)


class MONGOSettings(BaseSettings):
    MONGO_URI: str = config("MONGO_URI", default="mongodb://mongo:27017/")
    MONGO_DB: str = config("MONGO_DB", default="DB")
    MONGO_USER: str | None = config("MONGO_USER", default=None)
    MONGO_PASS: str | None = config("MONGO_PASS", default=None)


class FirstUserSettings(BaseSettings):
    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="admin@admin.com")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="!Ch4ng3Th1sP4ssW0rd!")


class Settings(AppSettings, ShortServiceSettings, MONGOSettings, RedisSettings,CelerySettings,CryptSettings, FirstUserSettings, AnalyticsSettings):
    pass


settings = Settings()
