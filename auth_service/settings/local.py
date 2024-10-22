"""
Local settings
"""

from datetime import timedelta

from .common import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = True

SECRET_KEY = os.getenv(  # noqa
    "SECRET_KEY", "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"
)

ALLOWED_HOSTS = ["*"]

HOST = "http://localhost:8000/"
DEFAULT_TENANT_HOST = "localhost"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("DB_NAME", "auth_service"),  # noqa
        "USER": os.getenv("DB_USERNAME", "postgres"),  # noqa
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),  # noqa
        "HOST": os.getenv("DB_HOST", "localhost"),  # noqa
        "PORT": os.getenv("DB_PORT", 5434),  # noqa
    }
}

# CORS config
CORS_ORIGIN_ALLOW_ALL = True

# JWT config
JWT_PRIVATE_KEY = (
    open(f"{BASE_DIR}/settings/example_key/private_key.pem").read()  # noqa
    if os.path.isfile(f"{BASE_DIR}/settings/example_key/private_key.pem")  # noqa
    else None
)
JWT_PUBLIC_KEY = (
    open(f"{BASE_DIR}/settings/example_key/public_key.pem").read()  # noqa
    if os.path.isfile(f"{BASE_DIR}/settings/example_key/public_key.pem")  # noqa
    else None
)

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
CELERY_BROKER_URL = "amqp://guest:guest@localhost"

OAUTH_CLIENTS = {
    "GOOGLE": {
        "TOKEN_URL": "https://oauth2.googleapis.com/token",
        "INFO_URL": "https://www.googleapis.com/oauth2/v3/userinfo",
        "CALLBACK_URL": os.getenv("GOOLE_CALLBACK_URL", "http://localhost"),  # noqa
        "CLIENT_ID": os.getenv(  # noqa
            "GOOGLE_CLIENT_ID",
            "785199163527-gsmd6erevavb198bi6k1nec34dm9epve.apps.googleusercontent.com",
        ),  # noqa
        "CLIENT_SECRET": os.getenv(  # noqa
            "GOOGLE_CLIENT_SECRET", "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"
        ),  # noqa
    }
}

CONSOLE_SERVICE_URL = ""
ROOT_API_KEY = ""
