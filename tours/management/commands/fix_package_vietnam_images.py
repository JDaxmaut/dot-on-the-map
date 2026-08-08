"""
python manage.py fix_package_vietnam_images

Перепривязывает фото к уже созданной странице пакетного тура по Вьетнаму:
hero-галерея и изображения отелей ищутся в библиотеке изображений по названиям.
"""
from django.core.management.base import BaseCommand


SLUG = "vietnam-s-nadezhnym-prinimayushchim-turoperatorom"

HERO_FILENAMES = [
    "pexels-haneul-trac-246343735-38720555.jpg",
    "pexels-quang-nguyen-vinh-222549-6346639.jpg",
    "pexels-quang-nguyen-vinh-222549-6875008.jpg",
    "pexels-wanderarch-18893625.jpg",
    "pexels-yukophotography-36636305.jpg",
]


class Command(BaseCommand):
    help = "Восстанавливает фото у пакетного тура по Вьетнаму по названиям изображений."

    def handle(self, *args, **options):
        from wagtail.images import get_image_model
        from tours.models import PackageTourPage

        page = PackageTourPage.objects.filter(slug=SLUG).first()
        if not page:
            self.stderr.write(f"Страница не найдена: {SLUG}")
            return

        Image = get_image_model()

        # Hero-галерея в исходном порядке
        hero_imgs = []
        for fname in HERO_FILENAMES:
            img = Image.objects.filter(title__endswith=fname).first()
            if img:
                hero_imgs.append(("image", img))
                self.stdout.write(f"  OK hero: {fname} ->id={img.pk}")
            else:
                self.stdout.write(f"  НЕТ hero: {fname}")

        # Отели: название изображения = «Отель {курорт} — {название отеля}»
        sections = []
        for b in page.hotel_sections:
            v = b.value
            hotels = []
            for h in v.get("hotels") or []:
                img = Image.objects.filter(
                    title=f"Отель {v.get('resort')} — {h.get('name')}"
                ).first()
                if img is None:
                    img = Image.objects.filter(
                        title__contains=h.get("name", "")[:30]
                    ).first()
                hotels.append({
                    "name": h.get("name"),
                    "type": h.get("type"),
                    "description": h.get("description"),
                    "image": img,
                })
                self.stdout.write(
                    f"  {'OK' if img else 'НЕТ'} отель: {h.get('name')}"
                )
            sections.append(("section", {
                "resort": v.get("resort"),
                "hotels": hotels,
            }))

        page.hero_images = hero_imgs
        page.hotel_sections = sections
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS("OK Страница сохранена и опубликована."))
