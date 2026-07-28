"""
python manage.py create_tour_chengdu_zhangjiajie

Создаёт TourPage «Аватар и Магический город» с загрузкой фото из папки.
Idempotent: если тур уже существует — пропускает.
"""
import os
import io
import datetime

from django.core.management.base import BaseCommand


SLUG = "avatir-i-magicheskiy-gorod"
PHOTOS_DEFAULT = r"C:\Users\dxmta\Desktop\tours"

HERO_FILENAMES = [
    "pexels-abdoo-35143804.jpg",
    "pexels-abdoo-35171760.jpg",
    "pexels-david-tran-1629960371-34683501.jpg",
    "pexels-david-tran-1629960371-34683510.jpg",
    "pexels-snow-chang-2148891262-31670757.jpg",
]

GALLERY_FILENAMES = [
    "pexels-gokhan-gol-62274-12662166.jpg",
    "pexels-hujason-21632070.jpg",
    "pexels-madzery-34923136 2.jpg",
    "pexels-quang-nguyen-vinh-222549-14023041.jpg",
    "pexels-quang-nguyen-vinh-222549-6871873.jpg",
    "pexels-vietnamcows-29981576.jpg",
]

GALLERY_CAPTIONS = {
    "pexels-gokhan-gol-62274-12662166.jpg": "Тяньмэньшань",
    "pexels-hujason-21632070.jpg": "Озеро Баофэн",
    "pexels-madzery-34923136 2.jpg": "Хунъядун",
    "pexels-quang-nguyen-vinh-222549-14023041.jpg": "Чэнду",
    "pexels-quang-nguyen-vinh-222549-6871873.jpg": "Чжанцзяцзе",
    "pexels-vietnamcows-29981576.jpg": "Панды",
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
    help = "Создаёт тур «Аватар и Магический город» с загрузкой фото в Wagtail."

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
            self.stderr.write("CatalogPage не найдена. Сначала запустите populate_db.")
            return

        photos_dir = options["photos"]

        self.stdout.write("Загружаю фото в Wagtail…")

        hero_images = []
        for fname in HERO_FILENAMES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю (нет файла): {fname}")
                continue
            title = f"Аватар-Магическийгород — hero — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"chengdu_zhangjiajie_hero_{fname}.jpg")
                hero_images.append(img)
                self.stdout.write(f"  OK hero: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        gallery_imgs = []
        for fname in GALLERY_FILENAMES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю (нет файла): {fname}")
                continue
            title = f"Аватар-Магическийгород — галерея — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"chengdu_zhangjiajie_gallery_{fname}.jpg")
                gallery_imgs.append(img)
                self.stdout.write(f"  OK gallery: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        self.stdout.write("Создаю страницу тура…")

        tour = TourPage(
            title="Аватар и Магический город",
            slug=SLUG,
            location="Китай · Чэнду · Чунцин · Фуронг · Чжанцзяцзе",
            summary=(
                "Экскурсионный тур в Китай на блоках Sichuan Airlines: горы Аватара, "
                "Тяньмэньшань, стеклянный мост, Долина панд и вечерний Чунцин. "
                "11 дней на полупансионе с русскоязычным гидом. "
                "Даты заездов: до 14.12.26 (пн, ср)."
            ),
            description=(
                "<p>Экскурсионные туры в Китай по маршруту: Чэнду — Чунцин — Фуронг — "
                "Чжанцзяцзе — Чэнду. Перелет рейсами Sichuan Airlines из Москвы.</p>"
                "<p>Два варианта программы:</p>"
                "<p><strong>Стандарт</strong> — вылеты по средам до 26.08.26. "
                "1 ночь в Фуронге, 3 ночи в Чжанцзяцзе. Включено шоу дронов в Чунцине.</p>"
                "<p><strong>Лайт</strong> — вылеты по понедельникам с 07.09.26 до 14.12.26. "
                "4 ночи в Чжанцзяцзе, без Фуронга.</p>"
            ),
            highlights=[
                ("item", "Национальный лесной парк Чжанцзяцзе — горы Аватара"),
                ("item", "Тяньмэньшань: Небесные врата и канатная дорога"),
                ("item", "Большой каньон и стеклянный мост Чжанцзяцзе"),
                ("item", "Древний город Фуронг — «висящий на водопаде»"),
                ("item", "Долина панд / НИЦ по охране больших панд"),
                ("item", "Ночной Чунцин: Хунъядун и монорельс Лицзыба"),
                ("item", "Храм Ухоу и древняя улица Цзиньли в Чэнду"),
            ],
            duration="11 дней / 10 ночей",
            group_size="до 15 человек",
            group_size_max=15,
            comfort="Отели 4–5*",
            difficulty="Лёгкая",
            price_from="от $1 861",
            country_tag="china",
            hero_images=[("image", img) for img in hero_images],
            itinerary=[
                ("day", {
                    "day_number": "1",
                    "title": "Перелет в Китай",
                    "description": (
                        "<p>Вылет в Чэнду рейсом 3U-8888 авиакомпании Sichuan Airlines "
                        "из аэропорта Шереметьево.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "2",
                    "title": "Прибытие в Чэнду · Экскурсия по городу",
                    "description": (
                        "<p>Прибытие в Чэнду. Трансфер в отель. Во второй половине дня — "
                        "посещение переулков Куаньчжайсянцзы (эпоха Цин), чай «гайвань», "
                        "Крытый мост, ночные виды города и улица баров.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "3",
                    "title": "Переезд в Чунцин · Лицзыба · Хунъядун",
                    "description": (
                        "<p>Переезд в Чунцин на высокоскоростном поезде. "
                        "Станция Лицзыба — метро, проходящее сквозь здание. "
                        "Творческий парк Элин Эрчан (панорамы Янцзы и Цзялина). "
                        "Вечером — ночной вид Хунъядуна.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "4",
                    "title": "Достопримечательности Чунцина",
                    "description": (
                        "<p>Древний город Цыцикоу, храм Баолунсы, пешеходная улица Цзефанбэй.</p>"
                        "<p><em>Стандарт:</em> световое шоу дронов «Очаровательный Чунцин» + "
                        "3D-монорельс.</p>"
                        "<p><em>Лайт:</em> свободное время, шопинг, речные прогулки.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "5",
                    "title": "Переезд в Чжанцзяцзе · Древний город Фуронг",
                    "description": (
                        "<p>Переезд на высокоскоростном поезде в Чжанцзяцзе. "
                        "Древний город Фуронг — «висящий на водопаде». "
                        "С наступлением темноты — золотая подсветка и шелест водопадов.</p>"
                        "<p><em>Стандарт:</em> заселение в отель Фуронга. "
                        "<em>Лайт:</em> возвращение в отель Чжанцзяцзе.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "6",
                    "title": "Горы Аватара",
                    "description": (
                        "<p>Дегустация чая Чжанцзяцзе. Экскурсия в национальный лесной парк: "
                        "лифт Байлун (рекорд Гиннесса), район Юаньцзяцзе («парящие горы»), "
                        "гора Тяньцзы, канатная дорога, ущелье «Золотой Кнут», "
                        "Галерея десяти ли.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "7",
                    "title": "Тяньмэньшань",
                    "description": (
                        "<p>Национальный лесной парк Тяньмэньшань: фуникулер, пещера "
                        "Тяньмэньдун, стеклянная тропа, эскалатор, канатная дорога. "
                        "Ужин в стилизованном ресторане.</p>"
                        "<p><em>Опционально:</em> шоу «Вечная любовь».</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "8",
                    "title": "Большой каньон · Стеклянный мост · Башня 72 чудес",
                    "description": (
                        "<p>Большой каньон Чжанцзяцзе и стеклянный мост (самый длинный "
                        "и высокий в мире). Художественная галерея Цзюньшэн. "
                        "Ночная прогулка у Башни 72 чудес — архитектурный комплекс "
                        "в стилистике подвесных домов на сваях.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "9",
                    "title": "Возвращение в Чэнду · Храм Ухоу · Цзиньли",
                    "description": (
                        "<p>Перелет или переезд на поезде в Чэнду. "
                        "Храм Ухоу (эпоха Троецарствия). Древняя улица Цзиньли.</p>"
                        "<p><em>Опционально:</em> сычуанская опера с сменой масок.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "10",
                    "title": "Панды · Книжный магазин · Музей парчи",
                    "description": (
                        "<p><em>Стандарт:</em> природный парк «Долина панд». "
                        "<em>Лайт:</em> НИЦ по охране больших панд в Дуцзянъяне.</p>"
                        "<p>Книжный магазин Чжуншу Гэ (иммерсивное арт-пространство). "
                        "Музей парчи Цзиньсю + мастер-класс. "
                        "Пешеходные улицы Чуньсилу и Тайгули.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "11",
                    "title": "Вылет домой",
                    "description": (
                        "<p>Трансфер в аэропорт. Вылет в Москву рейсом 3U3887 "
                        "авиакомпании Sichuan Airlines.</p>"
                    ),
                    "image": None,
                }),
            ],
            accommodation=[
                ("item", {
                    "name": "Отель 4–5*, Чэнду",
                    "type": "Отель · 3 ночи (1 + 2)",
                    "description": "Полупансион (завтрак + ужин). Размещение в начале и конце тура.",
                    "image": None,
                }),
                ("item", {
                    "name": "Отель 4*, Чунцин",
                    "type": "Отель · 2 ночи",
                    "description": "Полупансион. Рядом с основными достопримечательностями.",
                    "image": None,
                }),
                ("item", {
                    "name": "Отель 4*, Фуронг (Стандарт) / Чжанцзяцзе (Лайт)",
                    "type": "Отель · 1–4 ночи",
                    "description": "Стандарт: 1 ночь в Фуронге. Лайт: 4 ночи в Чжанцзяцзе.",
                    "image": None,
                }),
                ("item", {
                    "name": "Отель 4*, Чжанцзяцзе",
                    "type": "Отель · 3 ночи",
                    "description": "Полупансион. База для экскурсий по горам Аватара и Тяньмэньшань.",
                    "image": None,
                }),
            ],
            included=[
                ("item", "Медицинская страховка (покрытие $40 000)"),
                ("item", "Туристическая страховка в Китае (300 000 юаней)"),
                ("item", "Международный перелет (гарантированные блоки Sichuan Airlines)"),
                ("item", "Проживание на полупансионе (завтраки + ужины)"),
                ("item", "Билеты 2-класса на высокоскоростные поезда: Чэнду–Чунцин–Чжанцзяцзе–Чэнду"),
                ("item", "Все переезды по программе"),
                ("item", "Экскурсии с русскоязычным гидом"),
                ("item", "Входные билеты по маршруту"),
            ],
            excluded=[
                ("item", "Страховка от невыезда (3% или 5% от стоимости тура)"),
                ("item", "Личные расходы и всё, что не указано явно в программе"),
                ("item", "Дополнительные экскурсии по желанию"),
                ("item", "Чаевые"),
            ],
            cancel_policy=[
                ("item", {
                    "period": "50% при бронировании",
                    "description": "50% стоимости тура в течение 3 календарных дней после подтверждения",
                    "refund_percent": 50,
                }),
                ("item", {
                    "period": "Полная оплата за 40 дней",
                    "description": "Полная оплата за 40 календарных дней до вылета",
                    "refund_percent": 0,
                }),
            ],
            force_majeure_note=(
                "При форс-мажоре (стихийные бедствия, закрытие границ) — "
                "возврат 100% независимо от срока."
            ),
            what_to_bring=[
                ("item", "Загранпаспорт (срок действия минимум 6 месяцев)"),
                ("item", "Виза в Китай (оформляется заранее)"),
                ("item", "Удобная обувь для ходьбы по паркам и горам"),
                ("item", "Солнцезащитный крем и головной убор"),
                ("item", "Лёгкая одежда для тёплой погоды"),
                ("item", "Наличные (юани и доллары)"),
                ("item", "Страховой полис"),
            ],
            faq=[
                ("item", {
                    "question": "Чем отличаются варианты Стандарт и Лайт?",
                    "answer": (
                        "<p><strong>Стандарт</strong> — вылеты по средам до 26.08.26. "
                        "1 ночь в Фуронге, 3 ночи в Чжанцзяцзе. Включено шоу дронов.</p>"
                        "<p><strong>Лайт</strong> — вылеты по понедельникам с 07.09.26 до 14.12.26. "
                        "4 ночи в Чжанцзяцзе, без Фуронга.</p>"
                    ),
                }),
                ("item", {
                    "question": "Нужна ли виза в Китай?",
                    "answer": "<p>Да, виза оформляется заранее в консульстве или через визовый центр.</p>",
                }),
                ("item", {
                    "question": "Что включено в питание?",
                    "answer": "<p>Полупансион: завтраки и ужины в отелях на протяжении всего тура.</p>",
                }),
                ("item", {
                    "question": "Когда лучше ехать?",
                    "answer": "<p>Вылеты до 14.12.26: по средам (Стандарт) и понедельникам (Лайт).</p>",
                }),
            ],
            cta_heading="Готовы увидеть горы Аватара и Долину панд?",
            cta_button="Выбрать дату",
            seo_title="Тур Аватар и Магический город — Чэнду, Чунцин, Чжанцзяцзе, 11 дней | Точка на карте",
            search_description=(
                "Экскурсионный тур в Китай: Чэнду, Чунцин, Фуронг, Чжанцзяцзе — горы Аватара, "
                "Тяньмэньшань, Долина панд. 11 дней, полупансион, перелет Sichuan Airlines. "
                "Даты до 14.12.26. От $1 861."
            ),
        )

        catalog.add_child(instance=tour)
        tour.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"OK Тур создан: {tour.title}"))

        # Даты — Стандарт (ср, до 26.08.26)
        standard_dates = [
            datetime.date(2026, 5, 6),
            datetime.date(2026, 5, 13),
            datetime.date(2026, 5, 20),
            datetime.date(2026, 5, 27),
            datetime.date(2026, 6, 3),
            datetime.date(2026, 6, 10),
            datetime.date(2026, 6, 17),
            datetime.date(2026, 6, 24),
            datetime.date(2026, 7, 1),
            datetime.date(2026, 7, 8),
            datetime.date(2026, 7, 15),
            datetime.date(2026, 7, 22),
            datetime.date(2026, 7, 29),
            datetime.date(2026, 8, 5),
            datetime.date(2026, 8, 12),
            datetime.date(2026, 8, 19),
            datetime.date(2026, 8, 26),
        ]
        # Даты — Лайт (пн, 07.09–14.12.26)
        light_dates = [
            datetime.date(2026, 9, 7),
            datetime.date(2026, 9, 14),
            datetime.date(2026, 9, 21),
            datetime.date(2026, 9, 28),
            datetime.date(2026, 10, 5),
            datetime.date(2026, 10, 12),
            datetime.date(2026, 10, 19),
            datetime.date(2026, 10, 26),
            datetime.date(2026, 11, 2),
            datetime.date(2026, 11, 9),
            datetime.date(2026, 11, 16),
            datetime.date(2026, 11, 23),
            datetime.date(2026, 11, 30),
            datetime.date(2026, 12, 7),
            datetime.date(2026, 12, 14),
        ]

        for d in standard_dates:
            end = d + datetime.timedelta(days=10)
            TourDate.objects.create(
                page=tour, start_date=d, end_date=end,
                price=152450, currency="RUB",
                total_spots=15, spots_left=15,
            )
        for d in light_dates:
            end = d + datetime.timedelta(days=10)
            TourDate.objects.create(
                page=tour, start_date=d, end_date=end,
                price=152450, currency="RUB",
                total_spots=15, spots_left=15,
            )
        self.stdout.write(f"  OK даты тура: {len(standard_dates)} стандарт + {len(light_dates)} лайт")

        for i, img in enumerate(gallery_imgs):
            fname = GALLERY_FILENAMES[i] if i < len(GALLERY_FILENAMES) else ""
            TourGalleryImage.objects.create(
                page=tour, image=img,
                caption=GALLERY_CAPTIONS.get(fname, ""),
                sort_order=i,
            )
        self.stdout.write(f"  OK галерея: {len(gallery_imgs)} фото")

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! Тур доступен по адресу /catalog/{SLUG}/"
        ))
