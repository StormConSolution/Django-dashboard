import os
from decouple import config
from unipath import Path
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = Path(__file__).parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False)

# load production server from .env
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'drf_yasg',
    'data',
    'authentication',  # Enable the inner app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'dashboard.urls'

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
    ('ar', 'Arabic (العربية)'),
    ('zh', 'Chinese (中文)'),
    ('da', 'Danish (Dansk)'),
    ('nl', 'Dutch (Nederlands)'),
    ('en', 'English'),
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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'dashboard/static'),
)
#############################################################
#############################################################

# Variables expected from settings_local. Docker overrides these with the
# values from .env.prod but when testing locally outside a container, these
# values can be overriden.
SQL_DATABASE = 'dashboard'
SQL_HOST = 'localhost'
SQL_PASSWORD = ''
SQL_PORT = 5432
SQL_USER = 'postgres'

DEBUG = False

try:
    from .settings_local import *
except:
    pass

# Used by the add_data view. Set proper values in settings_local
API_HOST = os.environ.get('REPUSTATE_API_HOST', API_HOST)
APIKEY = os.environ.get('REPUSTATE_APIKEY', APIKEY)

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.postgresql_psycopg2"),
        "NAME": os.environ.get("SQL_DATABASE", SQL_DATABASE),
        "USER": os.environ.get("SQL_USER", SQL_USER),
        "PASSWORD": os.environ.get("SQL_PASSWORD", SQL_PASSWORD),
        "HOST": os.environ.get("SQL_HOST", SQL_HOST),
        "PORT": os.environ.get("SQL_PORT", SQL_PORT),
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
}

LOGGING_CONFIG = None