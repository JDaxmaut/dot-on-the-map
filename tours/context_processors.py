from django.conf import settings


def site_settings(request):
    from tours.models import LegalPage
    return {
        "YANDEX_METRIKA_ID": getattr(settings, "YANDEX_METRIKA_ID", ""),
        "TELEGRAM_URL": getattr(settings, "TELEGRAM_URL", "https://t.me/tochka_nakarte"),
        "legal_pages": LegalPage.objects.live().order_by("title"),
    }
