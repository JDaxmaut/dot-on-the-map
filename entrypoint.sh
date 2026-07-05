#!/bin/sh
set -e

mkdir -p /app/data
python manage.py migrate --noinput
exec gunicorn tochka.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
