#!/bin/bash

if [ "$CONTAINER_BEHAVIOUR" == "DJANGO" ]
  then
    python manage.py collectstatic --noinput
    python manage.py makemigrations
    python manage.py migrate

    gunicorn -w 1 --bind 0.0.0.0:8000 app.wsgi

elif [ "$CONTAINER_BEHAVIOUR" == "CELERY" ]
  then
    celery -A app worker -l info
fi
