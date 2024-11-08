# staging.py

from .base import *
from .DEFAULT import DEFAULT_HEADERS

DEBUG = False


# STATIC_ROOT = os.path.join(BASE_DIR, "static/")
# STATIC_URL = '/static/'

CORS_ALLOW_HEADERS = DEFAULT_HEADERS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]