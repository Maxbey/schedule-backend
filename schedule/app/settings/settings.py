from configurations import values

from .base import BaseSettings


class Production(BaseSettings):
    DEBUG = False
    SECRET_KEY = values.SecretValue(environ_prefix='')

    DATABASES = values.DatabaseURLValue(
        environ_required=True,
        environ_prefix=''
    )

    INSTALLED_APPS = BaseSettings.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    MIDDLEWARE_CLASSES = BaseSettings.MIDDLEWARE_CLASSES + \
        ['corsheaders.middleware.CorsMiddleware']

    CORS_ALLOW_CREDENTIALS = True

    ALLOWED_HOSTS = ['*']

    CORS_ORIGIN_ALLOW_ALL = True


class Develop(BaseSettings):
    DEBUG = True
    SECRET_KEY = 'secret'

    INSTALLED_APPS = BaseSettings.INSTALLED_APPS + [
        'django_extensions',
        'django_nose'
    ]


class Test(BaseSettings):
    DEBUG = True
    SECRET_KEY = 'secret'

    INSTALLED_APPS = BaseSettings.INSTALLED_APPS + [
        'django_extensions',
        'django_nose'
    ]

    BROKER_TRANSPORT = 'redis'
    BROKER_URL = 'url'
    CELERY_RESULT_BACKEND = 'url'
