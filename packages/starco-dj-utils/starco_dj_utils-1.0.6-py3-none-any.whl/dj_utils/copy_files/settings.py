import os
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()
settings.INSTALLED_APPS+=[
    'rest_framework',
    'django_celery_beat',
    'rest_framework.authtoken',
]

BASE_DIR = settings.BASE_DIR
#############################################
DEBUG = bool(int(str(os.getenv('DEBUG', 0))))
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(' ')
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(' ')
#############################################
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'
#############################################
postgresql = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv("POSTGRE_DB_NAME"),
    'USER': os.getenv("POSTGRE_USER"),
    'PASSWORD': os.getenv("POSTGRE_PASSWORD"),
    'HOST': os.getenv("POSTGRE_HOST"),
    'PORT': os.getenv("POSTGRE_PORT"),
}
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv("CACHE_URL"),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
#############################################
import sys
import colorlog

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'colored',
        },
    },

    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}
#############################################
# Celery settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
#############################################
# settings.DATABASES['default'] = postgresql
#############################################

