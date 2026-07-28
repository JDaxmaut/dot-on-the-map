"""
python manage.py create_tour_vietnam_cambodia

Создаёт TourPage «Новогодний побег во Вьетнам и Камбоджу» с загрузкой фото из папки.
Idempotent: если тур уже существует — пропускает.

Запуск:
    python manage.py create_tour_vietnam_cambodia
    python manage.py create_tour_vietnam_cambodia --photos "C:/path/to/photos"
"""
import os
import io
import datetime

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile


SLUG = "novogodniy-pobeg-vo-vetnam-i-kambodzhu"
PHOTOS_DEFAULT = r"C:\Users\dxmta\Desktop\tours"

# Все фото из папки тура (hero — первые 5, галерея — остальные)
HERO_FILENAMES = [
    "pexels-101599977-11055162.jpg",
    "pexels-33843172-7060048.jpg",
    "pexels-dmitriy-causelove-218646814-15415915.jpg",
    "pexels-frank-van-dijk-121009207-36818622.jpg",
    "pexels-kelly-19063349.jpg",
]

GALLERY_FILENAMES = [
    "pexels-lathinh-17787137.jpg",
    "pexels-nino-okruashvili-2149536237-37388158.jpg",
    "pexels-phat-tr-ng-1662052981-38695397.jpg",
    "pexels-quang-nguyen-vinh-222549-14021868 (3).jpg",
    "pexels-quang-nguyen-vinh-222549-2134272.jpg",
    "pexels-sergk1-15890550.jpg",
    "pexels-sergk1-15890735.jpg",
    "pexels-the-old-path-white-clouds-2162663424-38736809.jpg",
    "pexels-ti-u-b-o-tr-ng-41366219-7336586.jpg",
    "pexels-tomas-malik-793526-1660996.jpg",
]

GALLERY_CAPTIONS = {
    "pexels-lathinh-17787137.jpg": "Дельта Меконга",
    "pexels-nino-okruashvili-2149536237-37388158.jpg": "Храмы Ангкора",
    "pexels-phat-tr-ng-1662052981-38695397.jpg": "Хошимин",
    "pexels-quang-nguyen-vinh-222549-14021868 (3).jpg": "Камбоджа",
    "pexels-quang-nguyen-vinh-222549-2134272.jpg": "Вьетнам",
    "pexels-sergk1-15890550.jpg": "Пномпень",
    "pexels-sergk1-15890735.jpg": "Ханой",
    "pexels-the-old-path-white-clouds-2162663424-38736809.jpg": "Озеро Тонлесап",
    "pexels-ti-u-b-o-tr-ng-41366219-7336586.jpg": "Сиемреап",
    "pexels-tomas-malik-793526-1660996.jpg": "Остров Ко Руссей",
}


def load_image_file(path):
    """Открывает JPEG, возвращает байты JPEG."""
    from PIL import Image as PILImage
    ext = os.path.splitext(path)[1].lower()
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
    """Создаёт Wagtail Image из байт через temp-файл."""
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
    help = "Создаёт тур «Новогодний побег во Вьетнам и Камбоджу» с загрузкой фото в Wagtail."

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

        # ── Загрузка фото ────────────────────────────────────
        self.stdout.write("Загружаю фото в Wagtail…")

        hero_images = []
        for fname in HERO_FILENAMES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю (нет файла): {fname}")
                continue
            title = f"Вьетнам-Камбоджа — hero — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"vietnam_cambodia_hero_{fname}.jpg")
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
            title = f"Вьетнам-Камбоджа — галерея — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"vietnam_cambodia_gallery_{fname}.jpg")
                gallery_imgs.append(img)
                self.stdout.write(f"  OK gallery: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        # ── Создание страницы тура ───────────────────────────
        self.stdout.write("Создаю страницу тура…")

        tour = TourPage(
            title="Новогодний побег во Вьетнам и Камбоджу",
            slug=SLUG,
            location="Вьетнам · Камбоджа",
            summary=(
                "Комбинированный авторский тур по Юго-Восточной Азии на Новый год: "
                "Хошимин, Дельта Меконга, храмы Ангкора, остров Ко Руссей и вечерний Ханой. "
                "15 дней в минигруппе до 10 человек с русскоязычным гидом."
            ),
            description=(
                "<p>Комбинированный групповой тур по Юго-Восточной Азии на Новый год "
                "по авторскому маршруту: Хошимин — Дельта Меконга — Сиемреап — храмы "
                "Ангкора — Ко Руссей — Пномпень — Ханой.</p>"
                "<p>Путешествие в минигруппе — до 10 человек! Экскурсии с русскоязычным "
                "гидом по программе тура.</p>"
            ),
            highlights=[
                ("item", "Экскурсия по Хошимину"),
                ("item", "Дельта Меконга на катере и джонке"),
                ("item", "Храмы Ангкора и рассвет в Ангкор Ват"),
                ("item", "Озеро Тонлесап и плавучая деревня"),
                ("item", "Встреча Нового года на острове Ко Руссей"),
                ("item", "Круиз по Меконгу на закате в Пномпене"),
                ("item", "Вечерний Ханой и железнодорожная улица"),
            ],
            duration="15 дней / 14 ночей",
            group_size="до 10 человек",
            group_size_max=10,
            comfort="Бутик-отели 4–5*",
            difficulty="Лёгкая",
            price_from="от $4 845",
            country_tag="vietnam",
            hero_images=[("image", img) for img in hero_images],
            itinerary=[
                ("day", {
                    "day_number": "1",
                    "title": "Перелет во Вьетнам",
                    "description": (
                        "<p>Вылет из аэропорта Шереметьево в Хошимин рейсами Vietnam Airlines, "
                        "стыковка в Ханое. Блочные места экономического класса.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "2",
                    "title": "Хошимин",
                    "description": (
                        "<p>Прибытие в Хошимин. Экскурсия по городу: прогулка по улице Донгкхой, "
                        "Центральное почтовое отделение Сайгона, Собор Сайгонской Богоматери. "
                        "Заселение в отель Silverland Yen Hotel 4*.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "3",
                    "title": "Дельта Меконга",
                    "description": (
                        "<p>Экскурсия в дельту Меконга: посещение пагоды Виньчанг, прогулка "
                        "на моторной лодке по реке, мастерская кокосовых сладостей, дегустация "
                        "тропических фруктов, обед, прогулка на сампане по узким каналам.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "4",
                    "title": "Перелет в Сиемреап",
                    "description": (
                        "<p>Свободное утро в Хошимине. Перелет в Сиемреап. Встреча с гидом, "
                        "ужин в ресторане отеля 5*, короткая прогулка по городу.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "5",
                    "title": "Храмы Бантэй Срэй и Бенг Миле · Озеро Тонлесап",
                    "description": (
                        "<p>Посещение храма Бантэй срэй (розовый песчаник), храма Бенг Миле "
                        "(затерянный в джунглях), обед в кхмерской деревне, катание на лодке "
                        "по озеру Тонлесап, плавучая вьетнамская деревня на закате.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "6",
                    "title": "Храмы Ангкора",
                    "description": (
                        "<p>Рассвет в храме Ангкор Ват. Экскурсия по храмам: Та Пром "
                        "(поглощенный джунглями), Ангкор Тхом, Байон (многоликие башни), "
                        "Та Кео. Возвращение в отель после 14 часов.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "7",
                    "title": "Перелет на остров Ко Руссей · Новый год",
                    "description": (
                        "<p>Вылет из Сиемреапа в Сиануквиль. Переправа на катере на остров "
                        "Ко Руссей. Заселение в отель Jati Koh Russey 5*. Встреча Нового года "
                        "на пляже тропического острова с новогодним ужином.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "8–10",
                    "title": "Ко Руссей — пляжный отдых",
                    "description": (
                        "<p>Свободные дни для пляжного отдыха на острове Ко Руссей. "
                        "По желанию за доплату: заказ дополнительных экскурсий.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "11",
                    "title": "Трансфер в Пномпень · Круиз по Меконгу",
                    "description": (
                        "<p>Трансфер на катере в порт Сиануквиля, переезд в Пномпень (3 часа). "
                        "Заселение в отель TRIBE Phnom Penh 4*. В 16:00 — круиз по Меконгу "
                        "на закате вдоль набережной столицы Камбоджи с ужином на корабле.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "12",
                    "title": "Пномпень",
                    "description": (
                        "<p>Прогулка по Пномпеню на тук-туках: пагода Ват Пном, Королевский "
                        "дворец, Серебряная пагода, Монумент Независимости, кофе с видами.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "13",
                    "title": "Перелет в Ханой · Вечерняя экскурсия",
                    "description": (
                        "<p>Свободное утро в Пномпене. Перелет в Ханой. Вечерняя прогулка "
                        "вокруг озера Хоанкьем, Старый квартал, ужин с Фо и ханойским кофе "
                        "с яйцом, железнодорожная улица.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "14",
                    "title": "Обзорная экскурсия по Ханою",
                    "description": (
                        "<p>Храм Литературы, озеро Ван, Флаговая башня, площадь Бадинь, "
                        "храм Куан Тхань, пагода Чанкуок. Обед в местном ресторане.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "15",
                    "title": "Завершение тура",
                    "description": (
                        "<p>Трансфер в аэропорт Ханоя. Вылет в Москву рейсом Vietnam Airlines, "
                        "гарантированные блочные места. Прибытие в аэропорт Шереметьево.</p>"
                    ),
                    "image": None,
                }),
            ],
            accommodation=[
                ("item", {
                    "name": "Silverland Yen Hotel 4*",
                    "type": "Отель · 2 ночи",
                    "description": "Executive Park View, Хошимин. Расположен в центре города.",
                    "image": None,
                }),
                ("item", {
                    "name": "Angkor Palace 5*",
                    "type": "Отель · 3 ночи",
                    "description": "Deluxe номер, Сиемреап. Рядом с храмами Ангкора.",
                    "image": None,
                }),
                ("item", {
                    "name": "Jati Koh Russey 5*",
                    "type": "Отель · 4 ночи",
                    "description": "Garden Pavilion, остров Ко Руссей. Пляжный отдых.",
                    "image": None,
                }),
                ("item", {
                    "name": "TRIBE Phnom Penh Post Office Square 4*",
                    "type": "Отель · 2 ночи",
                    "description": "Comfort Room, Пномпень. В самом центре города.",
                    "image": None,
                }),
                ("item", {
                    "name": "Le Jardin Haute Couture Hotel 4*",
                    "type": "Отель · 2 ночи",
                    "description": "Double Premier, Ханой. Уютный отель в столице Вьетнама.",
                    "image": None,
                }),
            ],
            included=[
                ("item", "Медицинская страховка (покрытие $40 000)"),
                ("item", "Внутренние перелеты"),
                ("item", "Проживание на экскурсионном маршруте на базе завтрака"),
                ("item", "3 обеда по программе"),
                ("item", "4 ужина по программе (включая новогодний ужин)"),
                ("item", "Экскурсии с русскоязычным гидом по программе"),
                ("item", "Входные билеты в места по программе"),
                ("item", "Трансферы с русскоязычным гидом, машина с кондиционером"),
            ],
            excluded=[
                ("item", "Международный перелет (включается или нет в зависимости от типа подпакета)"),
                ("item", "Виза в Камбоджу"),
                ("item", "Страховка от невыезда (3% или 5% от стоимости тура)"),
                ("item", "Личные расходы и все, что не указано явно в программе"),
                ("item", "Чаевые"),
                ("item", "Дополнительные экскурсии по желанию"),
            ],
            cancel_policy=[
                ("item", {
                    "period": "За 30+ дней",
                    "description": "Возврат стоимости тура за вычетом фактически понесённых расходов",
                    "refund_percent": 80,
                }),
                ("item", {
                    "period": "За 14–29 дней",
                    "description": "Возврат 50% стоимости тура",
                    "refund_percent": 50,
                }),
                ("item", {
                    "period": "За 7–13 дней",
                    "description": "Возврат 20% стоимости тура",
                    "refund_percent": 20,
                }),
                ("item", {
                    "period": "Менее 7 дней",
                    "description": "Возврат не производится",
                    "refund_percent": 0,
                }),
            ],
            force_majeure_note=(
                "При форс-мажоре (стихийные бедствия, закрытие границ) — "
                "возврат 100% независимо от срока."
            ),
            what_to_bring=[
                ("item", "Загранпаспорт (срок действия минимум 6 месяцев)"),
                ("item", "Виза в Камбоджу (оформляется заранее или по прилёту)"),
                ("item", "Удобная обувь для храмовых комплексов"),
                ("item", "Солнцезащитный крем и головной убор"),
                ("item", "Лёгкая одежда для тропического климата"),
                ("item", "Наличные (доллары и местная валюта)"),
                ("item", "Зарядное устройство (обратите внимание: Vietnam Airlines запрещает портативные зарядки)"),
                ("item", "Страховой полис"),
            ],
            faq=[
                ("item", {
                    "question": "Нужна ли виза в Камбоджу?",
                    "answer": "<p>Да, виза в Камбоджу оформляется по прилёту или заранее. Стоимость — около $30.</p>",
                }),
                ("item", {
                    "question": "Включен ли международный перелет?",
                    "answer": "<p>В зависимости от выбранного типа подпакета. Международный рейс Vietnam Airlines: Москва — Ханой — Хошимин и обратно.</p>",
                }),
                ("item", {
                    "question": "Какой размер группы?",
                    "answer": "<p>Минигруппа до 10 человек. Путешествие проходит с русскоязычным гидом на протяжении всего маршрута.</p>",
                }),
                ("item", {
                    "question": "Что включено в питание?",
                    "answer": "<p>Завтраки в отелях, 3 обеда и 4 ужина по программе, включая новогодний ужин на острове Ко Руссей.</p>",
                }),
            ],
            cta_heading="Готовы встретить Новый год в Азии?",
            cta_button="Выбрать дату",
            seo_title="Новогодний тур во Вьетнам и Камбоджу — 15 дней | Точка на карте",
            search_description=(
                "Авторский тур по Вьетнаму и Камбодже на Новый год 2027: "
                "Хошимин, Дельта Меконга, храмы Ангкора, остров Ко Руссей, "
                "Пномпень, Ханой. 15 дней, группа до 10 человек. От $4 845."
            ),
        )

        catalog.add_child(instance=tour)
        tour.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"OK Тур создан: {tour.title}"))

        # ── Даты тура ────────────────────────────────────────
        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2026, 12, 25),
            end_date=datetime.date(2027, 1, 8),
            price=396900,
            currency="RUB",
            total_spots=10,
            spots_left=10,
        )
        self.stdout.write("  OK дата тура: 25.12.2026 — 08.01.2027")

        # ── Галерея ─────────────────────────────────────────
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
