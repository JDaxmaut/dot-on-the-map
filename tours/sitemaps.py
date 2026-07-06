import re

from django.conf import settings
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap


def sitemap(request):
    response = wagtail_sitemap(request)
    if settings.WAGTAILADMIN_BASE_URL and response.status_code == 200:
        response.render()
        content = response.content.decode("utf-8")
        content = re.sub(
            r"https?://[^/]+(?::\d+)?",
            settings.WAGTAILADMIN_BASE_URL.rstrip("/"),
            content,
        )
        response.content = content.encode("utf-8")
        response["Content-Length"] = str(len(response.content))
    return response
