"""
python manage.py create_tour_phuquoc_hanoi
"""
import os
import io
import datetime

from django.core.management.base import BaseCommand


SLUG = "novogodniy-tur-phu-quoc-hanoi"
PHOTOS_DEFAULT = r"C:\Users\dxmta\Desktop\tours"

HERO_FILENAMES = [
    "pexels-h-u-quy-t-626368657-37059838.jpg",
    "pexels-hoa-le-dinh-1615807371-28448335.jpg",
    "pexels-kirandeepsingh-33587102.jpg",
    "pexels-quang-nguyen-vinh-222549-26742979.jpg",
    "pexels-quang-nguyen-vinh-222549-14012627.jpg",
]

GALLERY_FILENAMES = [
    "pexels-hducdev-17111168.jpg",
    "pexels-linh-tran-553086511-35056585.jpg",
    "pexels-natalia-23512369-6769701.jpg",
    "pexels-nguy-n-huy-1091648355-20656446.jpg",
    "pexels-petra-nesti-1766376-31187735.jpg",
]

GALLERY_CAPTIONS = {
    "pexels-hducdev-17111168.jpg": "Ханой",
    "pexels-linh-tran-553086511-35056585.jpg": "Ниньбинь",
    "pexels-natalia-23512369-6769701.jpg": "Фукуок",
    "pexels-nguy-n-huy-1091648355-20656446.jpg": "Ханой",
    "pexels-petra-nesti-1766376-31187735.jpg": "Фукуок",
}


def load_image_file(path):
    from PIL import Image as PILImage
    pil_img = PILImage.open(path)
    try:
        from PIL import ImageOps
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass
    if pil_img.mode in ("RGBA", "P", "LA"):
        pil_img = pil_img.convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


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
        tmp.seek(0)
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
    help = "Создаёт тур «Фукуок — Ханой: новогодний тур во Вьетнам»."

    def add_arguments(self, parser):
        parser.add_argument(
            "--photos",
            default=PHOTOS_DEFAULT,
            help="Путь к папке с фотографиями тура",
        )

    def handle(self, *args, **options):
        from tours.models import CatalogPage, TourPage, TourDate, TourGalleryImage

        if TourPage.objects.filter(slug=SLUG).exists():
            self.stdout.write(f"Тур уже существует: {SLUG}")
            return

        catalog = CatalogPage.objects.first()
        if not catalog:
            self.stderr.write("CatalogPage не найдена.")
            return

        photos_dir = options["photos"]

        self.stdout.write("Загружаю фото…")

        hero_images = []
        for fname in HERO_FILENAMES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю: {fname}")
                continue
            title = f"Фукуок-Ханой — hero — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"phuquoc_hanoi_hero_{fname}.jpg")
                hero_images.append(img)
                self.stdout.write(f"  OK hero: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        gallery_imgs = []
        for fname in GALLERY_FILENAMES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю: {fname}")
                continue
            title = f"Фукуок-Ханой — галерея — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"phuquoc_hanoi_gallery_{fname}.jpg")
                gallery_imgs.append(img)
                self.stdout.write(f"  OK gallery: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        self.stdout.write("Создаю страницу тура…")

        tour = TourPage(
            title="Фукуок — Ханой: новогодний тур во Вьетнам",
            slug=SLUG,
            location="Вьетнам · Фукуок · Ханой · Ниньбинь",
            summary=(
                "Комбинированный новогодний тур с пляжным отдыхом на Фукуоке "
                "и экскурсиями по Ханою и Ниньбиню. Перелет на блоках Vietnam Airlines. "
                "Даты заездов: 28.12.26, 30.12.26."
            ),
            description=(
                "<p>Новогодний тур во Вьетнам: пляжный отдых на Фукуоке + экскурсии "
                "по Ханою и Ниньбиню. Перелет на блоках Vietnam Airlines из Москвы.</p>"
                "<p><strong>Варианты заезда:</strong></p>"
                "<ul>"
                "<li><strong>28.12.26:</strong> Фукуок (8 ночей) — Ханой (2 ночи) — Ниньбинь</li>"
                "<li><strong>30.12.26:</strong> Фукуок (9 ночей) — Ханой (2 ночи) — Ниньбинь</li>"
                "</ul>"
            ),
            highlights=[
                ("item", "Пляжный отдых на острове Фукуок"),
                ("item", "Обзорная экскурсия по Ханою + прогулка на рикше"),
                ("item", "Ниньбинь: пагода Бай Динь, комплекс Чанган (ЮНЕСКО)"),
                ("item", "Пещера Муа и подъём на гору Нгоа Лонг"),
                ("item", "Перелет на блоках Vietnam Airlines из Москвы"),
                ("item", "Отель на выбор на Фукуоке"),
                ("item", "Русскоязычный гид на экскурсиях"),
            ],
            duration="12–13 дней",
            group_size="до 15 человек",
            group_size_max=15,
            comfort="Отель на выбор на Фукуоке + Pan Pacific 4* в Ханое",
            difficulty="Лёгкая",
            price_from="от $2 232",
            country_tag="vietnam",
            hero_images=[("image", img) for img in hero_images],
            itinerary=[
                ("day", {
                    "day_number": "1",
                    "title": "Вылет во Вьетнам",
                    "description": (
                        "<p>Вылет из Москвы (SVO) в Ханой рейсом Vietnam Airlines VN 062 "
                        "в 16:30. Стыковка в Ханое, пересадка на рейс до Фукуока.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "2",
                    "title": "Прибытие на Фукуок",
                    "description": (
                        "<p>Прибытие в аэропорт Фукуока. Встреча с водителем, "
                        "трансфер в отель. Заселение. Свободное время для отдыха "
                        "на пляже.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "3–9/10",
                    "title": "Пляжный отдых на Фукуоке",
                    "description": (
                        "<p>Свободные дни на острове Фукуок. Количество дней зависит "
                        "от выбранной даты вылета (28.12 — 8 ночей, 30.12 — 9 ночей).</p>"
                        "<p><em>Опционально:</em> снорклинг, канатная дорога Хонтхом "
                        "(самая длинная в мире), ночной рынок Dinh Cau, сафари-парк "
                        "Vinpearl, массаж у моря.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "10/11",
                    "title": "Перелет в Ханой · Экскурсия по городу",
                    "description": (
                        "<p>Выписка из отеля. Трансфер в аэропорт Фукуока. "
                        "Перелет в Ханой. Встреча с гидом: обед с Фо и кофе с яйцом. "
                        "Обзорная экскурсия: Храм Литературы, пагода на одном столбе, "
                        "площадь Бадинь. Часовая прогулка на рикше. Шёлковая улица.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "11/12",
                    "title": "Провинция Ниньбинь",
                    "description": (
                        "<p>Поездка в Ниньбинь: пагода Бай Динь (крупнейший буддийский "
                        "комплекс, 500 статуй архатов, 10-метровая бронзовая статуя "
                        "Будды). Обед. Комплекс Чанган (ЮНЕСКО) — 1,5–2 часа "
                        "прогулки на лодке по пещерам (съёмки «Конг: Остров черепа»). "
                        "Пещера Муа и подъём на гору Нгоа Лонг.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "12/13",
                    "title": "Вылет домой",
                    "description": (
                        "<p>Завтрак в отеле. Выписка в 06:00. Трансфер с гидом "
                        "в аэропорт Ханоя. Вылет в Москву рейсом Vietnam Airlines VN 063. "
                        "Прибытие в Шереметьево.</p>"
                    ),
                    "image": None,
                }),
            ],
            accommodation=[
                ("item", {
                    "name": "Отель на выбор, Фукуок",
                    "type": "Отель · 8–9 ночей",
                    "description": "План питания выбирается при бронировании. Широкий выбор отелей — от уютных бунгало до премиальных резортов.",
                    "image": None,
                }),
                ("item", {
                    "name": "Pan Pacific Hotel 4*",
                    "type": "Отель · 2 ночи",
                    "description": "Deluxe номер или аналогичный, Ханой. Завтраки включены.",
                    "image": None,
                }),
            ],
            included=[
                ("item", "Медицинская страховка (покрытие $40 000)"),
                ("item", "Международный перелет (гарантированные блоки Vietnam Airlines)"),
                ("item", "Внутренние перелеты"),
                ("item", "Проживание на Фукуоке с выбранным планом питания"),
                ("item", "2 ночи в Ханое на завтраках"),
                ("item", "2 обеда по программе"),
                ("item", "Экскурсии с русскоязычным гидом"),
                ("item", "Переезды по программе"),
            ],
            excluded=[
                ("item", "Страховка от невыезда (3% или 5% от стоимости тура)"),
                ("item", "Личные расходы и всё, что не указано явно"),
                ("item", "Чаевые"),
                ("item", "Дополнительные экскурсии по желанию"),
            ],
            cancel_policy=[
                ("item", {
                    "period": "Предоплата",
                    "description": "1 250 USD/чел в течение 3 дней после подтверждения",
                    "refund_percent": 0,
                }),
                ("item", {
                    "period": "Полная оплата до 01.11.26",
                    "description": "100% оплата до 1 ноября 2026. С 01.11.26 — удержание 100%",
                    "refund_percent": 0,
                }),
            ],
            force_majeure_note=(
                "При форс-мажоре (стихийные бедствия, закрытие границ) — "
                "возврат 100% независимо от срока."
            ),
            what_to_bring=[
                ("item", "Загранпаспорт (срок действия минимум 6 месяцев)"),
                ("item", "Купальник и лёгкая одежда для тропиков"),
                ("item", "Солнцезащитный крем"),
                ("item", "Удобная обувь для экскурсий"),
                ("item", "Наличные (доллары и донги)"),
                ("item", "Страховой полис"),
            ],
            faq=[
                ("item", {
                    "question": "Какие даты заездов?",
                    "answer": "<p>28.12.26 и 30.12.26. Разница — в количестве ночей на Фукуоке (8 или 9).</p>",
                }),
                ("item", {
                    "question": "Включён ли перелёт?",
                    "answer": "<p>Да, международный перелёт на блоках Vietnam Airlines из Москвы.</p>",
                }),
                ("item", {
                    "question": "Какой отель на Фукуоке?",
                    "answer": "<p>Вы выбираете отель и план питания при бронировании — от бунгало до премиальных резортов.</p>",
                }),
            ],
            cta_heading="Встретьте Новый год на тропическом острове!",
            cta_button="Выбрать дату",
            seo_title="Новогодний тур на Фукуок и в Ханой — 12/13 дней | Точка на карте",
            search_description=(
                "Новогодний тур во Вьетнам: пляжный отдых на Фукуоке + Ханой + Ниньбинь. "
                "Перелёт на Vietnam Airlines. Даты: 28.12.26, 30.12.26. От $2 232."
            ),
        )

        catalog.add_child(instance=tour)
        tour.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"OK Тур создан: {tour.title}"))

        # 28.12 → 12 дней (8 ночей Фукуок + 2 Ханой + вылет 08.01)
        TourDate.objects.create(
            page=tour, start_date=datetime.date(2026, 12, 28),
            end_date=datetime.date(2027, 1, 8),
            price=182850, currency="RUB",
            total_spots=15, spots_left=15,
        )
        # 30.12 → 13 дней (9 ночей Фукуок + 2 Ханой + вылет 11.01)
        TourDate.objects.create(
            page=tour, start_date=datetime.date(2026, 12, 30),
            end_date=datetime.date(2027, 1, 11),
            price=182850, currency="RUB",
            total_spots=15, spots_left=15,
        )
        self.stdout.write("  OK даты: 28.12.26 и 30.12.26")

        for i, img in enumerate(gallery_imgs):
            fname = GALLERY_FILENAMES[i] if i < len(GALLERY_FILENAMES) else ""
            TourGalleryImage.objects.create(
                page=tour, image=img,
                caption=GALLERY_CAPTIONS.get(fname, ""),
                sort_order=i,
            )
        self.stdout.write(f"  OK галерея: {len(gallery_imgs)} фото")

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! /catalog/{SLUG}/"
        ))
