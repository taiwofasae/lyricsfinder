
from lyricsproject import env


SECRET_KEY = env.get_key('SECRET_KEY')

DEBUG = env.get_key('DEBUG') == 'True'

allowed_hosts = env.get_key('ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts.split(',') if allowed_hosts else []

allowed_origins = env.get_key('CORS_ALLOWED_ORIGINS')
CORS_ALLOWED_ORIGINS = allowed_origins.split(',') if allowed_origins else []

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

STATIC_URL = env.get_key('STATIC_URL') or 'static/'

STATIC_ROOT = env.get_key('STATIC_ROOT')

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

Q_CLUSTER = {
    'name': 'lyricsapp',
    'workers': 4,
    'timeout': 60,
    'retry': 90,
    'queue_limit': 100,
    'bulk': 5,
    'sqs': {
        'aws_region': env.get_key('AWS_DEFAULT_REGION'),
        'aws_access_key_id': env.get_key('AWS_ACCESS_KEY_ID'),
        'aws_secret_access_key': env.get_key('AWS_SECRET_ACCESS_KEY')
    }
}

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

SEARCH = {
    "ONDEMAND" : env.get_key('SEARCH_ONDEMAND') == 'True'
}