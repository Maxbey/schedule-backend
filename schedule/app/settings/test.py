from .base import BaseSettings


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

    BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''
