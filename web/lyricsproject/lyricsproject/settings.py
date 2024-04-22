"""
Django settings for lyricsproject project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
from . import env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get_key('SECRET_KEY') or  'django-insecure--u2p9&---%h&2+uo5q2o9*)f8tmku$!*lc*zyv!gc$2!kg*r9i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if env.get_key('DEBUG') == 'True' else False

allowed_hosts = env.get_key('ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts.split(',') if allowed_hosts else []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lyricsapp.apps.LyricsappConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    'catalog.apps.CatalogConfig',
    'django_q'
   # 'django_apscheduler'
]

CRISPY_TEMPLATE_PACK = 'bootstrap5'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lyricsproject.urls'

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

WSGI_APPLICATION = 'lyricsproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env.get_key('MYSQL_DB_NAME'),
        'USER': env.get_key('MYSQL_DB_USER'),
        'PASSWORD': env.get_key('MYSQL_DB_PASSWORD'),
        'HOST': env.get_key('MYSQL_DB_HOST'),
        'PORT': env.get_int_key('MYSQL_DB_PORT')
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = env.get_key('STATIC_URL') or 'static/'

STATIC_ROOT = env.get_key('STATIC_ROOT')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

Q_CLUSTER = {
    'name': env.get_key('MONGO_DB_NAME'),
    'workers': 8,
    'timeout': 60,
    'retry': 70,
    'queue_limit': 100,
    'mongo': {
        'host': env.get_key('MONGO_DB_HOST'),
        'port': env.get_int_key('MONGO_DB_PORT')
    }
}

# Q_CLUSTER = {
#     'name': 'DjangORM',
#     'workers': 4,
#     'timeout': 90,
#     'retry': 120,
#     'queue_limit': 50,
#     'bulk': 10,
#     'orm': 'default'
# }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.get_key('LOG_LEVEL') or "ERROR",
    },
}

S3 = {
    "FOLDER": env.get_key('S3_FOLDER'),
    "BUCKET_NAME": env.get_key('S3_BUCKET_NAME')
}