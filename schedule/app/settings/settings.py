from configurations import values

from .base import BaseSettings


class Production(BaseSettings):
    DEBUG = False
    SECRET_KEY = values.SecretValue(environ_prefix='')

    DATABASES = values.DatabaseURLValue(
        environ_required=True,
        environ_prefix=''
    )

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': values.SecretValue(
                environ_prefix='', environ_name='REDIS_URL'
            ),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 30}
            }
        }
    }

    INSTALLED_APPS = BaseSettings.INSTALLED_APPS + [
        'raven.contrib.django.raven_compat'
    ]

    RAVEN_CONFIG = {
        'dsn': values.SecretValue(environ_prefix='', environ_name='RAVEN_DSN')
    }

    MIDDLEWARE_CLASSES = BaseSettings.MIDDLEWARE_CLASSES + \
        ['corsheaders.middleware.CorsMiddleware']

    CORS_ALLOW_CREDENTIALS = True

    ALLOWED_HOSTS = ['*']

    CORS_ORIGIN_ALLOW_ALL = True


class Develop(BaseSettings):
    DEBUG = True
    SECRET_KEY = 'secret'

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': values.SecretValue(
                environ_prefix='', environ_name='REDIS_URL'
            ),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 30}
            }
        }
    }

    RAVEN_CONFIG = {
        'dsn': values.SecretValue(environ_prefix='', environ_name='RAVEN_DSN')
    }

    INSTALLED_APPS = BaseSettings.INSTALLED_APPS + [
        'django_nose'
    ]


class Test(BaseSettings):
    DEBUG = True
    SECRET_KEY = 'secret'

    INSTALLED_APPS = BaseSettings.INSTALLED_APPS + [
        'django_nose'
    ]

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    BROKER_TRANSPORT = 'redis'
    REDIS_URL = 'url'
    RAVEN_DSN = ''
