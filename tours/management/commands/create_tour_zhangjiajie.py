"""
python manage.py create_tour_zhangjiajie

Создаёт TourPage «Чжанцзяцзе — Чунцин: горы Аватара» с загрузкой фото из папки.
Idempotent: если тур уже существует — пропускает.

Запуск:
    python manage.py create_tour_zhangjiajie
    python manage.py create_tour_zhangjiajie --photos "C:/path/to/photos"
"""
import os
import io
import datetime

from django.core.management.base import BaseCommand


SLUG = "chzhan-tsya-tsze-chuntsin"
PHOTOS_DEFAULT = r"C:\Users\dxmta\Desktop\tours"

HERO_FILENAMES = [
    "pexels-2157012850-35312440.jpg",
    "pexels-793260840-36967160.jpg",
    "pexels-abdoo-35143804 (2).jpg",
    "pexels-abdoo-35143804.jpg",
    "pexels-abdoo-35171760.jpg",
]

GALLERY_FILENAMES = [
    "pexels-david-tran-1629960371-34683501.jpg",
    "pexels-david-tran-1629960371-34683510.jpg",
    "pexels-david-tran-1629960371-34683512.jpg",
    "pexels-gokhan-gol-62274-12662166 (2).jpg",
    "pexels-gokhan-gol-62274-12662166.jpg",
    "pexels-hujason-21632070.jpg",
    "pexels-madzery-34923136 2.jpg",
    "pexels-quang-nguyen-vinh-222549-14023041.jpg",
    "pexels-quang-nguyen-vinh-222549-6871873.jpg",
]

GALLERY_CAPTIONS = {
    "pexels-david-tran-1629960371-34683501.jpg": "Чунцин",
    "pexels-david-tran-1629960371-34683510.jpg": "Чжанцзяцзе",
    "pexels-david-tran-1629960371-34683512.jpg": "Горы Аватара",
    "pexels-gokhan-gol-62274-12662166 (2).jpg": "Стеклянный мост",
    "pexels-gokhan-gol-62274-12662166.jpg": "Тяньмэньшань",
    "pexels-hujason-21632070.jpg": "Озеро Баофэн",
    "pexels-madzery-34923136 2.jpg": "Хунъядун",
    "pexels-quang-nguyen-vinh-222549-14023041.jpg": "Китай",
    "pexels-quang-nguyen-vinh-222549-6871873.jpg": "Чжанцзяцзе парк",
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
    help = "Создаёт тур «Чжанцзяцзе — Чунцин» с загрузкой фото в Wagtail."

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
            title = f"Чжанцзяцзе-Чунцин — hero — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"zhangjiajie_hero_{fname}.jpg")
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
            title = f"Чжанцзяцзе-Чунцин — галерея — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"zhangjiajie_gallery_{fname}.jpg")
                gallery_imgs.append(img)
                self.stdout.write(f"  OK gallery: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        self.stdout.write("Создаю страницу тура…")

        tour = TourPage(
            title="Чжанцзяцзе — Чунцин: горы Аватара",
            slug=SLUG,
            location="Китай · Чжанцзяцзе · Чунцин",
            summary=(
                "Экскурсионный тур в Китай на блоках TianJin Airlines: горы Аватара, "
                "Тяньмэньшань, стеклянный мост, озеро Баофэн и вечерний Чунцин. "
                "8 дней с завтраками, обедами и русскоязычным гидом."
            ),
            description=(
                "<p>Экскурсионный тур в Китай с посещением гор Аватара и отдыхом "
                "в Чунцине. Перелет на гарантированных рейсах авиакомпании "
                "TianJin Airlines из Москвы.</p>"
                "<p>В стоимость входят входные билеты: стеклянный мост Большого "
                "каньона Чжанцзяцзе, озеро Баофэн, пещера Хуанлун, лесной парк, "
                "подъемник Байлун, канатная дорога на гору Тяньцзы и гора Тяньмэнь.</p>"
            ),
            highlights=[
                ("item", "Национальный лесной парк Чжанцзяцзе — горы Аватара"),
                ("item", "Тяньмэньшань: самая длинная в мире канатная дорога и Небесные врата"),
                ("item", "Стеклянный мост «Юньтяньду» + VR-аттракцион"),
                ("item", "Озеро Баофэн с прогулкой на лодке"),
                ("item", "Ночной Чунцин: Хунъядун и улица Лицзыба"),
                ("item", "Перелет блоками TianJin Airlines из Москвы"),
                ("item", "Русскоязычный гид на протяжении всего тура"),
            ],
            duration="8 дней / 7 ночей",
            group_size="до 15 человек",
            group_size_max=15,
            comfort="Отели 4*",
            difficulty="Лёгкая",
            price_from="от $1 727",
            country_tag="china",
            hero_images=[("image", img) for img in hero_images],
            itinerary=[
                ("day", {
                    "day_number": "1",
                    "title": "Перелет в Китай",
                    "description": (
                        "<p>Вылет из Москвы в Чунцин рейсом GS7942 авиакомпании "
                        "Tianjin Airlines. Блочные места экономического класса. "
                        "Вылет из аэропорта Шереметьево в 16:40.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "2",
                    "title": "Прилет в Чунцин · Экскурсия по городу",
                    "description": (
                        "<p>Прибытие в Чунцин. Встреча в аэропорту, трансфер в отель, "
                        "заселение. После обеда — экскурсия: смотровая на улице Бэйбинь, "
                        "рельсовый транспорт в Лицзыба, площадь Цзефанбэй, башня Куйсин, "
                        "прогулка по улице на уровне 22 этажа.</p>"
                        "<p><em>Опционально за доплату:</em> павильон панд в зоопарке, "
                        "шоу «The Yangtze River Show».</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "3",
                    "title": "Переезд в Чжанцзяцзе · Озеро Баофэн",
                    "description": (
                        "<p>Переезд в Чжанцзяцзе на скоростном поезде (~2 часа). "
                        "Обед по прибытии. Экскурсия по озеру Баофэн — кристально "
                        "чистое озеро среди горных вершин, прогулка на лодке мимо "
                        "водопадов.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "4",
                    "title": "Тяньмэньшань",
                    "description": (
                        "<p>Экскурсия в Национальный лесопарк Тяньмэньшань. "
                        "Включено: большой фуникулер, стеклянная тропа, эскалаторы, "
                        "пещера «Тяньмэньдун», скоростная канатная дорога (7455 м, "
                        "28 минут). «Небесные врата» — пещера-арка на вершине горы, "
                        "«Лестница в небо» из 999 ступеней, «Дорога в Небо» — "
                        "горный серпантин с 99 поворотами.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "5",
                    "title": "Горы Аватара",
                    "description": (
                        "<p>Национальный лесной парк Чжанцзяцзе. Подъем на подъемнике "
                        "Байлун, район Юаньцзяцзе: колонна Цянькунь, мост «Первый "
                        "в Поднебесной». Спуск по канатной дороге горы Тяньцзышань, "
                        "прогулка вдоль ручья Золотой Кнут. Ужин в ресторане.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "6",
                    "title": "Стеклянный мост · Возвращение в Чунцин",
                    "description": (
                        "<p>Стеклянный мост «Юньтяньду» — самый длинный и высокий "
                        "стеклянный мост в мире + VR-аттракцион. Обед. Мастер-класс "
                        "по приготовлению чая (если хватит времени). Переезд в Чунцин "
                        "на поезде. По дороге — ночной вид на Хунъядун, 11-этажный "
                        "комплекс на скале.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "7",
                    "title": "Свободный день в Чунцине",
                    "description": (
                        "<p>Свободный день в Чунцине. Завтрак в отеле. Можно "
                        "прогуляться самостоятельно, посетить местные рестораны "
                        "и достопримечательности.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "8",
                    "title": "Вылет в Москву",
                    "description": (
                        "<p>Трансфер в аэропорт. Вылет в Москву рейсом GS7941 "
                        "авиакомпании Tianjin Airlines в 11:05. Прибытие в аэропорт "
                        "Шереметьево в 14:55.</p>"
                    ),
                    "image": None,
                }),
            ],
            accommodation=[
                ("item", {
                    "name": "Zhangjiajie Yunju 4*",
                    "type": "Отель · 3 ночи",
                    "description": "Standard номер, Чжанцзяцзе. Рядом с национальным парком.",
                    "image": None,
                }),
                ("item", {
                    "name": "Chongqing Wudeng 4*",
                    "type": "Отель · 3 ночи",
                    "description": "Или аналогичный, Чунцин. Удобное расположение для экскурсий.",
                    "image": None,
                }),
            ],
            included=[
                ("item", "Медицинская страховка (покрытие $40 000)"),
                ("item", "Международный перелет (гарантированные блоки TianJin Airlines)"),
                ("item", "Проживание на основе завтраков"),
                ("item", "4 обеда по программе"),
                ("item", "1 ужин по программе"),
                ("item", "Экскурсии по программе"),
                ("item", "Русскоязычный гид (8 часов в день, сверхурочно — $15/час)"),
                ("item", "Групповые трансферы"),
                ("item", "Билеты на поезда по программе (обычный класс)"),
                ("item", "Топливный сбор авиакомпании"),
                ("item", "Входные билеты: стеклянный мост, озеро Баофэн, пещера Хуанлун, лесной парк, подъемник Байлун, канатная дорога Тяньцзы, гора Тяньмэнь"),
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
                    "description": "Предоплата 50% стоимости тура",
                    "refund_percent": 50,
                }),
                ("item", {
                    "period": "Полная оплата за 31 день",
                    "description": "Полная оплата за 31 день до заезда",
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
                    "question": "Нужна ли виза в Китай?",
                    "answer": "<p>Да, виза оформляется заранее в консульстве или через визовый центр.</p>",
                }),
                ("item", {
                    "question": "Какие авиабилеты?",
                    "answer": "<p>Перелет на гарантированных блоках TianJin Airlines: Москва — Чунцин и обратно. Экономический класс.</p>",
                }),
                ("item", {
                    "question": "Что включено в питание?",
                    "answer": "<p>Завтраки в отелях, 4 обеда и 1 ужин по программе.</p>",
                }),
                ("item", {
                    "question": "Насколько сложный маршрут?",
                    "answer": "<p>Маршрут лёгкий. Основные переходы — на поездах и канатных дорогах. Есть свободный день в Чунцине для отдыха.</p>",
                }),
            ],
            cta_heading="Готовы увидеть горы Аватара?",
            cta_button="Выбрать дату",
            seo_title="Тур в Чжанцзяцзе и Чунцин — горы Аватара, 8 дней | Точка на карте",
            search_description=(
                "Экскурсионный тур в Китай: Чжанцзяцзе — горы Аватара, Тяньмэньшань, "
                "стеклянный мост, Чунцин. 8 дней, отели 4*, завтраки и обеды. "
                "Перелет из Москвы. От $1 727."
            ),
        )

        catalog.add_child(instance=tour)
        tour.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"OK Тур создан: {tour.title}"))

        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2026, 7, 28),
            end_date=datetime.date(2026, 8, 4),
            price=141480,
            currency="RUB",
            total_spots=15,
            spots_left=15,
        )
        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2026, 8, 7),
            end_date=datetime.date(2026, 8, 14),
            price=141480,
            currency="RUB",
            total_spots=15,
            spots_left=15,
        )
        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2026, 8, 14),
            end_date=datetime.date(2026, 8, 21),
            price=141480,
            currency="RUB",
            total_spots=15,
            spots_left=15,
        )
        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2026, 8, 25),
            end_date=datetime.date(2026, 9, 1),
            price=141480,
            currency="RUB",
            total_spots=15,
            spots_left=15,
        )
        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2026, 12, 28),
            end_date=datetime.date(2027, 1, 4),
            price=141480,
            currency="RUB",
            total_spots=15,
            spots_left=15,
        )
        self.stdout.write("  OK даты тура: 5 заездов (2026–2027)")

        for i, img in enumerate(gallery_imgs):
            fname = GALLERY_FILENAMES[i] if i < len(GALLERY_FILENAMES) else ""
            TourGalleryImage.objects.create(
                page=tour,
                image=img,
                caption=GALLERY_CAPTIONS.get(fname, ""),
                sort_order=i,
            )
        self.stdout.write(f"  OK галерея: {len(gallery_imgs)} фото")

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! Тур доступен по адресу /catalog/{SLUG}/"
        ))
