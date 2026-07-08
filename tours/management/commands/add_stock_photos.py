"""
python manage.py add_stock_photos

Добавляет стоковые горизонтальные фото в hero-слайдер тура «5 островов Индонезии».
Idempotent: проверяет по title — не дублирует.
"""
import io
import os

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

SLUG = "ekspeditsiya-5-ostrovov-indonezii"
PHOTOS_DIR = r"C:\Users\dxmta\AppData\Local\Temp\stock_photos"

# Только горизонтальные фото
STOCK_PHOTOS = [
    ("stock_gili_islands.jpg",    "Гили Траванган — вид с дроуна"),
    ("stock_komodo_hills.jpg",    "Архипелаг Комодо — холмы и бухта"),
    ("stock_komodo_dragons.jpg",  "Комодо — вараны на пляже"),
    ("stock_whale_shark.jpg",     "Сумбава — китовая акула"),
]


def upload_wagtail_image(title, image_bytes, filename):
    import tempfile
    from PIL import Image as PILImage
    from django.core.files import File
    from wagtail.images import get_image_model
    WagtailImage = get_image_model()

    existing = WagtailImage.objects.filter(title=title).first()
    if existing:
        return existing

    w, h = PILImage.open(io.BytesIO(image_bytes)).size

    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    try:
        tmp.write(image_bytes)
        tmp.flush()
        with open(tmp.name, "rb") as f:
            img = WagtailImage(title=title)
            img.file.save(filename, File(f), save=False)
        if not img.width:
            img.width = w
            img.height = h
        img.save()
    finally:
        tmp.close()
        os.unlink(tmp.name)
    return img


class Command(BaseCommand):
    help = "Добавляет стоковые фото в hero тура «5 островов Индонезии»."

    def handle(self, *args, **options):
        import sys
        sys.stdout.reconfigure(encoding="utf-8")

        from tours.models import TourPage

        tour = TourPage.objects.filter(slug=SLUG).first()
        if not tour:
            self.stderr.write(f"Тур не найден: {SLUG}")
            return

        self.stdout.write("Загружаю стоковые фото...")

        new_imgs = []
        for fname, title in STOCK_PHOTOS:
            src_name = fname.replace("stock_", "")
            src_path = os.path.join(PHOTOS_DIR, src_name)
            if not os.path.exists(src_path):
                self.stdout.write(f"  Нет файла: {src_path}")
                continue
            with open(src_path, "rb") as f:
                data = f.read()
            try:
                img = upload_wagtail_image(title, data, fname)
                new_imgs.append(img)
                self.stdout.write(f"  OK: {title} (id={img.pk})")
            except Exception as e:
                self.stdout.write(f"  ERR {fname}: {e}")

        if not new_imgs:
            self.stdout.write("Нет новых фото.")
            return

        # Добавляем к существующим hero_images
        # StreamChild объекты нельзя смешивать с tuples — конвертируем
        existing = [(block.block_type, block.value) for block in tour.hero_images]
        tour.hero_images = existing + [("image", img) for img in new_imgs]
        revision = tour.save_revision()
        revision.publish()

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Hero-слайдер: {len(list(tour.hero_images))} фото."
        ))
