import os
from django.core.management.base import BaseCommand
from tours.models import EntryRuleCountryPage


class Command(BaseCommand):
    help = "Загрузка текстовых заметок для страниц стран въезда из папки"

    def add_arguments(self, parser):
        parser.add_argument(
            "source_dir",
            nargs="?",
            default=r"C:\Users\dxmta\Desktop\flags"
        )

    def handle(self, *args, **options):
        source_dir = options["source_dir"]
        if not os.path.isdir(source_dir):
            self.stderr.write(f"Папка не найдена: {source_dir}")
            return

        pages = {p.country_code: p for p in EntryRuleCountryPage.objects.live().all()}
        uploaded = 0

        for filename in os.listdir(source_dir):
            if not filename.lower().endswith('.txt'):
                continue

            country_name = filename.rsplit(".", 1)[0].lower()

            # Map filenames to country codes
            FILENAME_MAP = {
                "nepa": "nepal",
                "south-korea": "korea",
            }
            country_code = FILENAME_MAP.get(country_name, country_name.replace("-", ""))

            filepath = os.path.join(source_dir, filename)
            page = pages.get(country_code)

            if not page:
                self.stdout.write(f"  Страница не найдена для {country_code} ({country_name})")
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if not text:
                self.stdout.write(f"  {country_name}: файл пуст")
                continue

            old_text = page.notes or ""
            if text == old_text:
                self.stdout.write(f"  {country_name}: нет изменений")
                continue

            page.notes = text
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  {country_name}: загружена заметка"))
            uploaded += 1

        self.stdout.write(self.style.SUCCESS(f"Готово! Загружено {uploaded} заметок"))