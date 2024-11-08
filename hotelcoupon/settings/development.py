# development.py

from .base import *

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]

CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
]

REST_FRAMEWORK = {
    # 'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ]
}

