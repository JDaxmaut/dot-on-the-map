import os
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.images.models import Image
from wagtail.models import Collection
from tours.models import EntryRuleCountryPage


FLAG_FILE_MAP = {
    "vietnam": ("vietnam(pics.1).jpg", "Вьетнам"),
    "indonesia": ("indonesia-2(pics.3).jpg", "Индонезия"),
    "china": ("China(pics.1).jpg", "Китай"),
    "cambodia": ("Cambodia(pics.1).jpg", "Камбоджа"),
    "japan": ("japan-2(pics.2).jpg", "Япония"),
    "laos": ("laos(pics.1).jpg", "Лаос"),
    "malaysia": ("malaysia-2(pics.2).jpg", "Малайзия"),
    "nepal": ("nepa-2l(pics.2).jpg", "Непал"),
    "philippines": ("philippines-2(pics.2).jpg", "Филиппины"),
    "thailand": ("thailand-2(pics.2).jpg", "Таиланд"),
    "korea": ("south-korea-2(pics.1).jpg", "Южная Корея"),
}


class Command(BaseCommand):
    help = "Загрузка флагов стран из папки C:/Users/dxmta/Desktop/flags"

    def add_arguments(self, parser):
        parser.add_argument("flags_dir", nargs="?", default=r"C:\Users\dxmta\Desktop\flags")

    def handle(self, *args, **options):
        flags_dir = options["flags_dir"]
        if not os.path.isdir(flags_dir):
            self.stderr.write(f"Папка не найдена: {flags_dir}")
            return

        root = Collection.get_first_root_node()
        collection = root.get_children().filter(name="Флаги стран").first()
        if not collection:
            collection = root.add_child(name="Флаги стран")

        pages = {p.country_code: p for p in EntryRuleCountryPage.objects.live().all()}

        for code, (filename, label) in FLAG_FILE_MAP.items():
            filepath = os.path.join(flags_dir, filename)
            if not os.path.isfile(filepath):
                self.stdout.write(f"  {label}: файл {filename} не найден")
                continue

            page = pages.get(code)
            if not page:
                self.stdout.write(f"  {label}: страница не найдена")
                continue

            existing = Image.objects.filter(title=f"flag-{code}").first()
            if existing:
                self.stdout.write(f"  {label}: уже загружен, привязываю")
                page.flag_image = existing
                page.save_revision().publish()
                continue

            with open(filepath, "rb") as f:
                name = f"flag-{code}.jpg"
                wagtail_image = Image(
                    title=f"flag-{code}",
                    file=File(f, name=name),
                    collection=collection,
                )
                wagtail_image.save()

            page.flag_image = wagtail_image
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  {label}: загружен {name}"))

        self.stdout.write(self.style.SUCCESS("Готово!"))