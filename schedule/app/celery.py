from __future__ import absolute_import

import os

from django.conf import settings
from celery.app.base import Celery
import configurations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.test')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')

configurations.setup()

app = Celery('app')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)