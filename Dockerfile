FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=tochka.settings \
    DEBUG=False \
    SECRET_KEY=build-placeholder-not-used-at-runtime

WORKDIR /app

# System deps for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev libpng-dev libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/media_bak/original_images

# Копируем исходники флагов в образ (бэкап для томов)
COPY media/original_images/ /app/media_bak/original_images/
COPY tours/seed_data/ /app/media_bak/seed_data/

# Collect static files at build time
RUN python manage.py collectstatic --noinput

EXPOSE 8002

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
