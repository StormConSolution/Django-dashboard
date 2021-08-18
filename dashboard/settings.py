import os
import sys
import urllib.parse

from decouple import config
from unipath import Path

SITE_URL = ""
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = Path(__file__).parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_NAME = "dashboard_sessionid"
# load production server from .env
ALLOWED_HOSTS = ['*']

ADMINS = (
    ('Martin Ostrovsky', 'martin@repustate.com'),
)

ADMIN_EMAIL = 'Repustate <admin@repustate.com>'

MANAGERS = ADMINS

INTERNAL_IPS = [
    '127.0.0.1',
]

UPLOAD_CSV_FROM_CLIENT = os.environ.get("UPLOAD_CSV_FROM_CLIENT", False)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'drf_yasg',
    'data',
    'authentication',  # Enable the inner app
    "customize",
    "markdownify",
    #'debug_toolbar',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
ROOT_URLCONF = 'dashboard.urls'
CORS_ORIGIN_ALLOW_ALL = True
LOGIN_REDIRECT_URL = "/login/"   # Route defined in data/urls.py
LOGOUT_REDIRECT_URL = "/login/"  # Route defined in data/urls.py

TEMPLATE_DIR = os.path.join(
    BASE_DIR, "dashboard/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.general_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'dashboard.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


LANGUAGES = (
    ('en', 'English'),
    ('ar', 'Arabic (العربية)'),
    ('zh', 'Chinese (中文)'),
    ('da', 'Danish (Dansk)'),
    ('nl', 'Dutch (Nederlands)'),
    ('fi', 'Finnish (Suomi)'),
    ('fr', 'French (Français)'),
    ('de', 'German (Deutsch)'),
    ('he', 'Hebrew (עִברִית)'),
    ('it', 'Italian (Italiano)'),
    ('id', 'Indonesian (Bahasa Indonesia)'),
    ('ja', 'Japanese (日本語)'),
    ('ko', 'Korean (한국어)'),
    ('no', 'Norwegian (Norsk)'),
    ('pl', 'Polish (Polski)'),
    ('pt', 'Portuguese (Português)'),
    ('ru', 'Russian (русский)'),
    ('es', 'Spanish (Español)'),
    ('sv', 'Swedish (Svenska)'),
    ('tr', 'Turkish (Türk)'),
    ('th', 'Thai (ไทย)'),
    ('vi', 'Vietnamese (Tiếng Việt)'),
    ('ur', 'Urdu (اردو)'),
)

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = "/var/www/static"
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media_root")
MEDIA_URL = '/media/'

# Max number of objects that can be deleted through the admin.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'dashboard/static'),
)

AUTHENTICATION_BACKENDS = (
    'dashboard.backends.CaseInsensitiveModelBackend',
    'django.contrib.auth.backends.ModelBackend',
    'dashboard.backends.GuestBackend',
)
#############################################################
#############################################################

# Variables expected from settings_local. Docker overrides these with the
# values from an .env file but when testing locally outside a container, these
# values can be overriden.

APIKEY = 'repustatedemopage'
API_HOST = 'https://api.repustate.com'
AUTH_HOST = 'https://www.repustate.com'

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'django-db'

DEBUG = os.environ.get("DEBUG", False)

HMAC_SECRET = ""

SERVER_NAME = "https://demo.repustate.com"

SQL_DATABASE = 'rdv2'
SQL_HOST = 'database'
SQL_PASSWORD = 'example'
SQL_PORT = 5432
SQL_USER = 'postgres'

TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''

ZENDESK_USER = ''
ZENDESK_PASSWORD = ''

MARKDOWNIFY_WHITELIST_TAGS = {
 'a', 'p', 'h1', 'h2', 'h3','h4', 'h5', 'h6', 'h7', 'ul', 'li', 'span', 'img',
 'div', 'abbr', 'acronym', 'em', 'blockquote', 'i', 'strong', 'ol', 'b', 'code'
}

try:
    from .settings_local import *
except:
    pass

FIREBASE_AUTH = os.environ.get('FIREBASE_AUTH', False)
REPUSTATE_WEBSITE = os.environ.get("REPUSTATE_WEBSITE", "")
REPUSTATE_LOGIN = os.environ.get("REPUSTATE_LOGIN", "")
API_HOST = os.environ.get('REPUSTATE_API_HOST', API_HOST)
APIKEY = os.environ.get('REPUSTATE_APIKEY', APIKEY)
API_HOST = os.environ.get('REPUSTATE_API_HOST', API_HOST)
AUTH_HOST = os.environ.get('AUTH_HOST', AUTH_HOST)
SERVER_NAME = os.environ.get('SERVER_NAME', SERVER_NAME)

if FIREBASE_AUTH:
    import firebase_admin
    firebase_admin.initialize_app()

FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
FIREBASE_STORAGE_BUKCET = os.environ.get("FIREBASE_STORAGE_BUKCET", "")
FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID", "")

FLATFILE_URL = urllib.parse.urljoin(SERVER_NAME, "/api/csv/")
HMAC_SECRET = os.environ.get('HMAC_SECRET', HMAC_SECRET)

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', TWILIO_ACCOUNT_SID)
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', TWILIO_AUTH_TOKEN)

ZENDESK_USER = os.environ.get('ZENDESK_USER', ZENDESK_USER)
ZENDESK_PASSWORD = os.environ.get('ZENDESK_PASSWORD', ZENDESK_PASSWORD)

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql_psycopg2"),
        "NAME": os.environ.get("SQL_DATABASE", SQL_DATABASE),
        "USER": os.environ.get("SQL_USER", SQL_USER),
        "PASSWORD": os.environ.get("SQL_PASSWORD", SQL_PASSWORD),
        "HOST": os.environ.get("SQL_HOST", SQL_HOST),
        "PORT": os.environ.get("SQL_PORT", 5432),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

# Email settings
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = "apikey"
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[Repustate] '
SERVER_EMAIL = "Repustate <info@repustate.com>"

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'dashboard.urls.api_info',
    'DEFAULT_API_URL': 'https://iq.repustate.com',
}

LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'file',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'tasks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
    'formatters': {
        'file': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
}

import logging.config
logging.config.dictConfig(LOGGING)
