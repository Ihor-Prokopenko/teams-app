import os
from pathlib import Path
from environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()
env_file_path = os.path.join(BASE_DIR, "../.env")

if not os.path.exists(env_file_path):
    env_file_path = os.path.join(BASE_DIR, "../.env.example")
env.read_env(env_file=env_file_path)

SECRET_KEY = env.str("SECRET_KEY", default="django-insecure-suspv&r)sdinhulqxrv3vl$ovu2ws(2tl3re4f_k4c_uj9&-mn")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'drf_yasg',
    'django_filters',

    'users',
    'teams_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'base.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# DRF

PAGINATION_PAGE_SIZE = 10


REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": PAGINATION_PAGE_SIZE,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Retrying

RETRY_MAX_ATTEMPTS = 3
RETRY_WAIT_FIXED = 1000
REQUEST_TIMEOUT = 5

# GOOGLE AUTH

BASE_URL = env.str("BASE_URL", default="")
GOOGLE_OAUTH2_CLIENT_ID = env.str("GOOGLE_OAUTH2_CLIENT_ID", default="")
GOOGLE_OAUTH2_CLIENT_SECRET = env.str("GOOGLE_OAUTH2_CLIENT_SECRET", default="")
GOOGLE_ID_TOKEN_INFO_URL = env.str("GOOGLE_ID_TOKEN_INFO_URL", default="")
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = env.str("GOOGLE_ACCESS_TOKEN_OBTAIN_URL", default="")
GOOGLE_USER_INFO_URL = env.str("GOOGLE_USER_INFO_URL", default="")
GOOGLE_AUTH_URL = env.str("GOOGLE_AUTH_URL", default="")
GOOGLE_SCOPE_EMAIL = env.str("GOOGLE_SCOPE_EMAIL", default="")
GOOGLE_SCOPE_PROFILE = env.str("GOOGLE_SCOPE_PROFILE", default="")

#

REGISTRATION_METHODS = [
    ('registration', 'Registration'),
    ('google', "Google"),
]
