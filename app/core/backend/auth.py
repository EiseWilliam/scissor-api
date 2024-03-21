from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi.security import OAuth2PasswordBearer, APIKeyCookie
from jose import jwt, JWTError
from app.core.cache.redis import redis
from app.core.config.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
REDIS_URL = settings.REDIS_URL
ACCESS_TOKEN_LIFETIME_SECONDS = int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())
REFRESH_TOKEN_LIFETIME_SECONDS = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
cookie_scheme = APIKeyCookie(name="token", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    correct_password: bool = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return correct_password


def hash_password(password: str) -> str:
    hashed_password: str = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashed_password


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + expires_delta
    else:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def recreate_access_token(refresh_token: str):
    data = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    access_token = create_access_token(data)
    return access_token

async def blacklist_access_token(token: str) -> bool:
    try:
        redis.set(f"blacklist:{token}", "true", ex=ACCESS_TOKEN_LIFETIME_SECONDS)
        return True
    except Exception:
        return False

    
async def blacklist_refresh_token(token: str) -> bool:
    try:
        redis.set(f"blacklist:{token}", "true", ex=REFRESH_TOKEN_LIFETIME_SECONDS)
        return True
    except Exception:
        return False

async def verify_token(token: str) -> Any | None:
    """Verify a JWT token and return TokenData if valid.

    Parameters
    ----------
    token: str
        The JWT token to be verified.
    db: AsyncSession
        Database session for performing database operations.

    Returns
    -------
    TokenData | None
        TokenData instance if the token is valid, None otherwise.
    """

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    else:
        if payload:
            expired = datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc)
            if expired:
                return None
            else:
                if await redis.exists(f"blacklist:{token}"):
                    return None
                return {"id": payload["sub"], "email": payload["email"]}