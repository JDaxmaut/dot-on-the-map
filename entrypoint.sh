#!/bin/sh
set -e

mkdir -p /app/data /app/media/original_images

# Копируем флаги из репо в том, если их нет
for f in /app/tours/seed_data/*.jpg /app/tours/seed_data/*.png; do
  [ -e "$f" ] || continue
  bn=$(basename "$f")
  [ -f "/app/media/original_images/$bn" ] || cp "$f" "/app/media/original_images/"
done

python manage.py migrate --noinput
python manage.py seed_production
python manage.py collectstatic --noinput

exec gunicorn tochka.wsgi:application \
    --bind 0.0.0.0:8002 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
