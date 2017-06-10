import os

from configurations import Configuration, values


class BaseSettings(Configuration):
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    ALLOWED_HOSTS = []

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'rest_framework',
        'rest_framework.authtoken',
        'corsheaders',
        'rest_auth',
        'django_extensions',
        'schedule'
    ]

    REST_SESSION_LOGIN = False

    MIDDLEWARE_CLASSES = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'app.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
    )

    WSGI_APPLICATION = 'app.wsgi.application'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

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

    LANGUAGE_CODE = 'en-us'

    SITE_ID = 1

    STATIC_URL = '/static/'
    STATIC_ROOT = 'staticfiles'

    BROKER_TRANSPORT = 'redis'
    BROKER_URL = values.Value(environ_prefix='', environ_name='REDIS_URL')
    CELERY_RESULT_BACKEND = values.Value(
        environ_required=True, environ_prefix='', environ_name='REDIS_URL'
    )

    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_ENABLE_UTC = True

    # The amount of learning hours per day.
    LESSON_HOURS = 6
    SELF_EDUCATION_HOURS = 2
