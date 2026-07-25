"""
python manage.py sync_documents

Удаляет все текущие Wagtail-документы и загружает новые из папки SOURCE_DIR.
"""
import os
import shutil

from django.core.management.base import BaseCommand
from django.core.files import File
from wagtail.documents import get_document_model

SOURCE_DIR = r"C:\Users\dxmta\Desktop\buba"


class Command(BaseCommand):
    help = "Удаляет все документы Wagtail и загружает новые из buba/"

    def handle(self, *args, **options):
        import sys
        sys.stdout.reconfigure(encoding="utf-8")

        Document = get_document_model()
        media_docs_dir = os.path.join("media", "documents")

        # 1. Удаляем старые документы из БД и с диска
        old_docs = Document.objects.all()
        count_old = old_docs.count()
        for doc in old_docs:
            if doc.file and os.path.isfile(doc.file.path):
                os.remove(doc.file.path)
                self.stdout.write(f"  Удалён файл: {doc.file.path}")
        old_docs.delete()
        self.stdout.write(self.style.WARNING(f"Удалено старых документов: {count_old}"))

        # 2. Загружаем новые документы из SOURCE_DIR
        os.makedirs(media_docs_dir, exist_ok=True)

        files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
        if not files:
            self.stdout.write(self.style.ERROR(f"Нет файлов в {SOURCE_DIR}"))
            return

        for fname in files:
            src = os.path.join(SOURCE_DIR, fname)
            title = os.path.splitext(fname)[0].replace("_", " ").replace("-", " ")
            with open(src, "rb") as f:
                doc = Document(title=title)
                doc.file.save(fname, File(f), save=False)
                doc.save()
            self.stdout.write(f"  Загружен: {fname} -> id={doc.pk}")

        self.stdout.write(self.style.SUCCESS(f"Готово! Загружено документов: {len(files)}"))
