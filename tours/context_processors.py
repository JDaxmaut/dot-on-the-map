from django.conf import settings


def site_settings(request):
    return {
        "YANDEX_METRIKA_ID": getattr(settings, "YANDEX_METRIKA_ID", ""),
        "TELEGRAM_URL": getattr(settings, "TELEGRAM_URL", "https://t.me/tochka_travel"),
    }
