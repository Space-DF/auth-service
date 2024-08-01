"""
Production settings
"""

from datetime import timedelta

from .common import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = os.getenv("ENV", default="dev") == "dev"  # noqa

SECRET_KEY = os.getenv(  # noqa
    "SECRET_KEY", "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"
)

ALLOWED_HOSTS = [os.getenv("ALLOWED_HOSTS", "*")]  # noqa

HOST = os.getenv("HOST", "http://localhost:8000/")  # noqa
DEFAULT_TENANT_HOST = os.getenv("DEFAULT_TENANT_HOST", "localhost")  # noqa

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("DB_NAME", "spacedf_auth_service"),  # noqa
        "USER": os.getenv("DB_USERNAME", "postgres"),  # noqa
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),  # noqa
        "HOST": os.getenv("DB_HOST", "localhost"),  # noqa
        "PORT": os.getenv("DB_PORT", 5432),  # noqa
    }
}

# CORS config
CORS_ALLOWED_ORIGINS = os.getenv(  # noqa
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

# JWT config
JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")  # noqa
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")  # noqa

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "RS256",
    "SIGNING_KEY": JWT_PRIVATE_KEY,
    "VERIFYING_KEY": JWT_PUBLIC_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("common.apps.refresh_tokens.jwts.CustomAccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(hours=1),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=7),
    "TOKEN_REFRESH_SERIALIZER": "common.apps.refresh_tokens.serializers.CustomTokenRefreshSerializer",
    "TOKEN_OBTAIN_SERIALIZER": "common.apps.refresh_tokens.serializers.CustomTokenObtainPairSerializer",
}
REFRESH_TOKEN_CLASS = "common.apps.refresh_tokens.jwts.CustomRefreshToken"  # nosec B105

# Celery
CELERY_BROKER_URL = os.getenv(  # noqa
    "CELERY_BROKER_URL", "amqp://guest:guest@localhost"
)
