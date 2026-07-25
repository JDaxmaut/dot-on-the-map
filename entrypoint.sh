#!/bin/sh
set -e

mkdir -p /app/data /app/media/original_images

# Восстанавливаем флаги из бэкапа в образе, если том пуст
if [ ! "$(ls -A /app/media/original_images 2>/dev/null)" ]; then
  cp -n /app/media_bak/original_images/* /app/media/original_images/ 2>/dev/null || true
fi

python manage.py migrate --noinput
python manage.py seed_production
python manage.py collectstatic --noinput

exec gunicorn tochka.wsgi:application \
    --bind 0.0.0.0:8002 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
