from datetime import datetime
from celery import shared_task

from .builder import ScheduleBuilder


@shared_task
def build_schedule(date):
    date_instance = datetime.strptime(date, '%Y-%m-%d')

    builder = ScheduleBuilder()
    builder.build(date_instance)