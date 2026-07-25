import os
import requests
import tempfile
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.images.models import Image
from wagtail.models import Collection
from tours.models import EntryRuleCountryPage


FLAG_MAP = {
    "vietnam": "vn",
    "indonesia": "id",
    "china": "cn",
    "cambodia": "kh",
    "japan": "jp",
    "laos": "la",
    "malaysia": "my",
    "nepal": "np",
    "philippines": "ph",
    "thailand": "th",
    "korea": "kr",
}


class Command(BaseCommand):
    help = "Загрузка флагов стран из flagcdn.com и привязка к страницам"

    def handle(self, *args, **options):
        root = Collection.get_first_root_node()
        collection = root.get_children().filter(name="Флаги стран").first()
        if not collection:
            collection = root.add_child(name="Флаги стран")

        pages = EntryRuleCountryPage.objects.live().all()
        for page in pages:
            code = FLAG_MAP.get(page.country_code)
            if not code:
                self.stdout.write(f"  Нет кода для {page.country_code}")
                continue

            url = f"https://flagcdn.com/256x192/{code}.png"
            self.stdout.write(f"  {page.country_name}: загрузка {url}...")

            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
            except Exception as e:
                self.stderr.write(f"  Ошибка загрузки {url}: {e}")
                continue

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name

            existing = Image.objects.filter(
                title__startswith=f"flag-{code}"
            ).first()

            if existing:
                self.stdout.write(f"    Уже загружен: {existing.title}")
                page.flag_image = existing
                page.save_revision().publish()
                os.unlink(tmp_path)
                continue

            with open(tmp_path, "rb") as f:
                wagtail_image = Image(
                    title=f"flag-{code}-{page.country_name.lower()}",
                    file=File(f, name=f"flag-{code}.png"),
                    collection=collection,
                )
                wagtail_image.save()

            page.flag_image = wagtail_image
            page.save_revision().publish()

            os.unlink(tmp_path)
            self.stdout.write(self.style.SUCCESS(f"    Флаг загружен и привязан к {page.country_name}"))

        self.stdout.write(self.style.SUCCESS("Готово!"))