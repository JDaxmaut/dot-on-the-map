from django.conf import settings
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap


class Sitemap(WagtailSitemap):
    def get_wagtail_site(self):
        from wagtail.models import Site

        site = Site.find_for_request(self.request)
        if site is None:
            site = Site.objects.select_related("root_page").get(is_default_site=True)

        if settings.WAGTAILADMIN_BASE_URL:
            site.root_url = settings.WAGTAILADMIN_BASE_URL.rstrip("/")

        return site
