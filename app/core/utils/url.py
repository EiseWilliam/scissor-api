import hashlib
import base64
import base62
from app.core.config.settings import settings

LENGTH = settings.URL_LENGTH
# def hash_url(url):
#     return base64.urlsafe_b64encode(hashlib.sha256(url.encode('utf-8')).digest()).decode('utf-8')[:10]

def hash_url(url):
    return base62.encodebytes(hashlib.sha256(url.encode('utf-8')).digest())[:LENGTH]