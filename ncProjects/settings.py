from pathlib import Path
import os, sys

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = os.path.dirname(__file__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['','localhost','127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_apscheduler',
#    'ncProjects.apps.instruction_osi',
#    'ncProjects.apps.fields_osi',
#    'ncProjects.apps.file_osi',
#    'ncProjects.apps.PCOS_app'
    'Starts',
    'Pcos',
    'Osi',
    'fdb_integration',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fdb_integration.middleware.AuthRequiredMiddleware',
]

FDB_SERVICES = {
    'auth_service': 'http://127.0.0.1:8000',
    'storage_service': 'http://127.0.0.1:8001',
    'data_service': 'http://localhost:8002',
    'visualization_service': 'http://localhost:8003',
    'missing_data_service': 'http://localhost:8004',
}

#добавлено мной для iframe
X_FRAME_OPTIONS = 'ALLOWALL'

ROOT_URLCONF = 'ncProjects.urls'

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
WSGI_APPLICATION = 'ncProjects.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'dev',
#         'USER': 'dev',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # 'fdb_postgres': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'main',
    #     'USER': 'postgres',
    #     'PASSWORD': 'postgres',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    # }
    'fdb_sqlite': {  # для FastAPI модуля
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'fastapi_db.sqlite3',
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://localhost:6379/",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Asia/Irkutsk'

USE_I18N = True

USE_L10N = True

USE_TZ = True



STATIC_DIR=os.path.join(PROJECT_ROOT,'static')
STATIC_ROOT = "/home//django-dev/static"
STATICFILES_DIRS = [STATIC_DIR,]
STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = '/home//django-dev/media'



# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
