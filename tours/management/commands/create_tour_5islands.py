"""
python manage.py create_tour_5islands

Создаёт TourPage «Тур-экспедиция: 5 островов Индонезии» с загрузкой фото из папки.
Горизонтальные фото ->hero_images (слайдер вверху).
Вертикальные фото   ->gallery_images (галерея внизу).
Idempotent: если тур уже существует — пропускает.

Запуск:
    python manage.py create_tour_5islands
    python manage.py create_tour_5islands --photos "C:/path/to/photos"
"""
import os
import io
import datetime

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile


SLUG = "ekspeditsiya-5-ostrovov-indonezii"
PHOTOS_DEFAULT = r"C:\Users\dxmta\Desktop\туро 3"

# Горизонтальные ->hero слайдер (w > h)
HERO_FILENAMES = [
    "IMG_4787 (2).PNG",
    "IMG_4788 (2).PNG",
    "IMG_4789 (2).PNG",
]

# Вертикальные ->галерея внизу
GALLERY_FILENAMES = [
    "IMG_4790 (2).PNG",
    "IMG_8341.HEIC",
    "IMG_8370.HEIC",
    "IMG_8381.HEIC",
    "IMG_9251.HEIC",
]


def load_image_file(path):
    """Открывает PNG/HEIC, возвращает (PIL.Image, bytes, ext)."""
    from PIL import Image as PILImage
    ext = os.path.splitext(path)[1].lower()
    if ext == ".heic":
        import pillow_heif
        heif = pillow_heif.open_heif(path)
        pil_img = heif.to_pillow()
    else:
        pil_img = PILImage.open(path)

    # Применить EXIF-поворот если есть
    try:
        from PIL import ImageOps
        pil_img = ImageOps.exif_transpose(pil_img)
    except Exception:
        pass

    # Конвертировать в JPEG
    if pil_img.mode in ("RGBA", "P", "LA"):
        pil_img = pil_img.convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=88)
    return buf.getvalue()


def upload_wagtail_image(title, image_bytes, filename):
    """Создаёт Wagtail Image из байт через temp-файл. Если уже есть — возвращает существующий."""
    import tempfile
    from PIL import Image as PILImage
    from django.core.files import File
    from wagtail.images import get_image_model
    WagtailImage = get_image_model()

    existing = WagtailImage.objects.filter(title=title).first()
    if existing:
        return existing

    # Узнаём размеры из байт
    w, h = PILImage.open(io.BytesIO(image_bytes)).size

    # Пишем в temp-файл и открываем как Django File —
    # только так ImageField корректно читает размеры через PIL
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    try:
        tmp.write(image_bytes)
        tmp.flush()
        tmp.seek(0)
        with open(tmp.name, "rb") as f:
            img = WagtailImage(title=title)
            img.file.save(filename, File(f), save=False)
        # На случай если ImageField не прочитал размеры
        if not img.width:
            img.width = w
            img.height = h
        img.save()
    finally:
        tmp.close()
        os.unlink(tmp.name)
    return img


class Command(BaseCommand):
    help = "Создаёт тур «5 островов Индонезии» с загрузкой фото в Wagtail."

    def add_arguments(self, parser):
        parser.add_argument(
            "--photos",
            default=PHOTOS_DEFAULT,
            help="Путь к папке с фотографиями тура",
        )

    def handle(self, *args, **options):
        from tours.models import CatalogPage, TourPage, TourDate, TourGalleryImage

        # ── Проверка идемпотентности ─────────────────────────
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
            title = f"5 островов — hero — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"5islands_hero_{fname}.jpg")
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
            title = f"5 островов — галерея — {fname}"
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(title, data, f"5islands_gallery_{fname}.jpg")
                gallery_imgs.append(img)
                self.stdout.write(f"  OK gallery: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        # ── Создание страницы тура ───────────────────────────
        self.stdout.write("Создаю страницу тура…")

        tour = TourPage(
            title="Тур-экспедиция: 5 островов Индонезии",
            slug=SLUG,
            location="Индонезия · Бали · Ломбок · Комодо · Сумбава · Гили",
            summary=(
                "14 дней по пяти островам: розовый пляж Комодо, снорклинг "
                "с китовыми акулами на Сумбаве, черепахи на Гили и ритуал "
                "очищения Мелукат на Бали."
            ),
            description=(
                "<p>Мы приготовили нечто потрясающее — тур-экспедицию по пяти "
                "островам Индонезии. Самолёт, рыбацкие лодки, катера и автотрип. "
                "Самые умопомрачительные локации, которые станут вашей мечтой.</p>"
                "<p><strong>Архипелаг Комодо.</strong> Нетронутая природа Индонезии. "
                "Национальный парк с редкими видами животных. Единственное в мире "
                "место, где живут комодские вараны — прямые потомки динозавров. "
                "Пляжи с розовым песком и встреча с гигантскими морскими скатами, "
                "размах крыльев которых достигает семи метров.</p>"
                "<p><strong>Сумбава.</strong> Фридайвинг и снорклинг с огромными "
                "китовыми акулами — до 18 метров в длину. Несмотря на размеры, "
                "они абсолютно безвредны для человека.</p>"
                "<p><strong>Гили Траванган.</strong> Остров без машин: только "
                "велосипеды и повозки с лошадьми. Белоснежный пляж, бирюзовая "
                "вода и снорклинг с черепахами, мантами, рифовыми акулами "
                "и баррракудами.</p>"
                "<p><strong>Бали.</strong> Изумрудный остров богов. Рисовые "
                "террасы Тегаллаланг, ритуал очищения Мелукат, кофе лювак "
                "и закаты на пляже Баланган.</p>"
                "<p>Океана в этом туре будет очень много — от Индийского до "
                "Тихого. Яркое приключение, которое запомнится на всю жизнь.</p>"
            ),
            highlights=[
                ("item", "Комодские вараны в национальном парке"),
                ("item", "Розовый пляж и снорклинг с мантами на Комодо"),
                ("item", "Снорклинг с китовыми акулами на Сумбаве"),
                ("item", "Гили без машин: черепахи, рифы и белый песок"),
                ("item", "Ритуал очищения Мелукат в святых источниках Бали"),
                ("item", "Рисовые террасы Тегаллаланг на рассвете"),
                ("item", "Закат и ужин на берегу Джимбарана"),
            ],
            duration="14 дней / 13 ночей",
            group_size="до 6 человек",
            group_size_max=6,
            comfort="Бутик-отели",
            difficulty="Умеренная",
            price_from="258 000 ₽",
            country_tag="bali",
            hero_images=[("image", img) for img in hero_images],
            itinerary=[
                ("day", {
                    "day_number": "День 1",
                    "title": "Прилёт · Заселение",
                    "description": (
                        "<p>Встреча в аэропорту Денпасар. Заселение в отель Mahagani. "
                        "Двухместные номера. Отдых и адаптация после перелёта.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 2",
                    "title": "Пляж Меласти · Закат на Балангане",
                    "description": (
                        "<p>После завтрака — живописный пляж Меласти и отдых "
                        "в пляжном клубе. Самый красивый закат встретим на утёсе "
                        "пляжа Баланган. День лёгкий и красивый.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 3",
                    "title": "Перелёт на Комодо · Лабуан Баджо",
                    "description": (
                        "<p>Внутренний перелёт на Комодо (1,5 часа). Размещение "
                        "в городке Лабуан Баджо. Прогулка по набережной, ужин "
                        "с видом на побережье.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 4",
                    "title": "Экспедиция по Комодо",
                    "description": (
                        "<p>В 6:30 — трансфер в порт с партнёром Red Whales. "
                        "Маршрут дня: смотровая на острове Падар, Розовый пляж "
                        "с уникальным розовым песком, встреча с комодскими "
                        "варанами, снорклинг с мантами на Манта-Поинт, "
                        "черепахи в бухте Тертл-Бэй на острове Сиаба-Бесар. "
                        "Вечером возвращение в отель.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 5",
                    "title": "Возвращение на Бали · Убуд",
                    "description": (
                        "<p>Перелёт из Лабуан Баджо на Бали. Заселение в отель "
                        "в Убуде. Отдых и свободное время — прогулка по вечернему "
                        "городу ремесленников.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 6",
                    "title": "Убуд · Рисовые террасы · Мелукат",
                    "description": (
                        "<p>Лес обезьян, рынок с уникальными сувенирами из дерева "
                        "и стекла. Обед в уютном кафе. Рисовые террасы Тегаллаланг "
                        "— качели над рисовыми полями с панорамным видом. "
                        "Обряд очищения Мелукат в святых источниках Себату — "
                        "балийский ритуал для тела и души.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 7",
                    "title": "Перелёт на Сумбаву",
                    "description": (
                        "<p>Утром выезжаем с вещами в аэропорт. Внутренний "
                        "перелёт на остров Сумбава — навстречу китовым акулам.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 8",
                    "title": "Снорклинг с китовыми акулами",
                    "description": (
                        "<p>01:00 — трансфер из отеля в деревню Лабуан Джамбу. "
                        "03:00 — выход на традиционной лодке в залив Сале-Бэй. "
                        "05:30 — посадка на лодку-паук, подготовка к снорклингу. "
                        "06:30–08:00 — снорклинг с китовыми акулами (до 18 м!) "
                        "и перекус на борту. Возвращение, отдых, обед по желанию.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 9",
                    "title": "Ломбок · Острова Гили",
                    "description": (
                        "<p>Перелёт с Сумбавы на Ломбок. Пересадка на рыбацкую "
                        "лодку — и на острова Гили. Размещение, вечерняя прогулка "
                        "по Гили Траванган.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 10–11",
                    "title": "Гили: снорклинг и пляжный отдых",
                    "description": (
                        "<p>Два полных дня на Гили Траванган — острове без машин "
                        "и моторов. Снорклинг или дайвинг с черепахами, мантами, "
                        "рифовыми акулами и барракудами. Белоснежные пляжи, "
                        "бирюзовая вода и закаты над вулканом Ринджани.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 12",
                    "title": "Возвращение на Бали · Бутет",
                    "description": (
                        "<p>На спидботе мчим с Гили обратно на Бали. "
                        "Заселение в отель на полуострове Букит.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 13",
                    "title": "Нуса-Дуа · Джимбаран",
                    "description": (
                        "<p>Активности на Нуса-Дуа: гидроциклы, флайборд, "
                        "парасейлинг или уроки сёрфинга. Вотерблоу — столб воды "
                        "высотой 10+ метров из океанской расщелины. Вечером — "
                        "прощальный ужин в ресторане на пляже Джимбаран "
                        "с морской кухней и закатом.</p>"
                    ),
                    "image": None,
                }),
                ("day", {
                    "day_number": "День 14",
                    "title": "Выезд · Аэропорт",
                    "description": (
                        "<p>Выселение из отеля в 12:00. Трансфер в аэропорт "
                        "Денпасар. До новых встреч, Бали — здесь ещё тысяча "
                        "мест, которые ждут вашего внимания.</p>"
                    ),
                    "image": None,
                }),
            ],
            accommodation=[
                ("item", {
                    "name": "Mahagani Hotel, Денпасар",
                    "type": "Отель · 2 ночи",
                    "description": "Комфортный отель в Денпасаре для старта и финиша экспедиции. Двухместные номера с завтраком.",
                    "image": None,
                }),
                ("item", {
                    "name": "Бутик-отель, Лабуан Баджо",
                    "type": "Бутик-отель · 2 ночи",
                    "description": "Отель в столице архипелага Комодо с видом на бухту. Идеальная база для дневных экспедиций.",
                    "image": None,
                }),
                ("item", {
                    "name": "Бутик-отель, Убуд",
                    "type": "Бутик-отель · 1 ночь",
                    "description": "Уютный отель в сердце Убуда — в городе мастеров и ремесленников Бали.",
                    "image": None,
                }),
                ("item", {
                    "name": "Бутик-отель, Сумбава Бесар",
                    "type": "Отель · 2 ночи",
                    "description": "База на Сумбаве для раннего выхода на снорклинг с китовыми акулами в заливе Сале-Бэй.",
                    "image": None,
                }),
                ("item", {
                    "name": "Гостевой дом, Гили Траванган",
                    "type": "Гостевой дом · 3 ночи",
                    "description": "Размещение на острове без машин: только велосипеды, пляж и бирюзовый океан за окном.",
                    "image": None,
                }),
                ("item", {
                    "name": "Бутик-отель, Букит",
                    "type": "Бутик-отель · 2 ночи",
                    "description": "Финальные ночи на южном полуострове Бали — рядом с Нуса-Дуа и пляжем Джимбаран.",
                    "image": None,
                }),
            ],
            included=[
                ("item", "Проживание в отелях (двухместные номера) с завтраками"),
                ("item", "Встреча и проводы в аэропорту Денпасар"),
                ("item", "Все наземные трансферы и переезды"),
                ("item", "Аренда автомобиля, топливо, работа водителя"),
                ("item", "Спидбот на острова Гили и обратно"),
                ("item", "Внутренние перелёты: Бали–Лабуан Баджо–Бали, Бали–Сумбава Бесар–Бали"),
                ("item", "Сопровождение русскоязычного куратора"),
                ("item", "Помощь в подборе и покупке авиабилетов"),
            ],
            excluded=[
                ("item", "Авиабилеты до Бали и обратно (от 60 000 ₽ в обе стороны)"),
                ("item", "Питание (кроме завтраков)"),
                ("item", "Входные билеты и эко-сборы"),
                ("item", "Страховка (обязательна — 9 000 ₽, медицина на Бали очень дорогая)"),
                ("item", "Виза (3 500 ₽, оплачивается в аэропорту в долларах)"),
                ("item", "Экскурсия по архипелагу Комодо на лодке Red Whales — 15 000 ₽ (включает трансфер, питание, снаряжение для снорклинга, билет в нацпарк, гида)"),
                ("item", "Снорклинг с китовыми акулами на Сумбаве — от 10 000 ₽ (трансфер, катер, гид, снаряжение, GoPro)"),
                ("item", "Личные расходы и дополнительные активности"),
            ],
            cancel_policy=[
                ("item", {
                    "period": "Предоплата",
                    "description": "Бронирование тура — предоплата 20 000 ₽. Предоплата не возвращается (уходит в бронь отеля)",
                    "refund_percent": 0,
                }),
                ("item", {
                    "period": "За 30+ дней",
                    "description": "Возврат оставшейся суммы за вычетом предоплаты",
                    "refund_percent": 80,
                }),
                ("item", {
                    "period": "За 14–29 дней",
                    "description": "Возврат 50% стоимости тура",
                    "refund_percent": 50,
                }),
                ("item", {
                    "period": "Менее 14 дней",
                    "description": "Возврат не производится",
                    "refund_percent": 0,
                }),
            ],
            force_majeure_note=(
                "При форс-мажоре (стихийные бедствия, закрытие границ) — "
                "возврат 100% независимо от срока. Программа тура может быть "
                "изменена по погодным условиям или в целях безопасности по "
                "усмотрению капитана. Компания не несёт ответственности за "
                "наличие мант на снорклинге, варанов в парке и китовых акул — "
                "это дикая природа."
            ),
            what_to_bring=[
                ("item", "Гидрокостюм или купальник + рашгард (защита от солнца)"),
                ("item", "Маска и трубка для снорклинга (или арендовать на месте)"),
                ("item", "Водонепроницаемый чехол для телефона"),
                ("item", "Солнцезащитный крем без хлора (экологичный, для нацпарков)"),
                ("item", "Лёгкая одежда с закрытыми плечами (для храмов)"),
                ("item", "Удобная обувь для трекинга по холмам Комодо"),
                ("item", "Наличные — рупии и доллары для виз и экскурсий"),
                ("item", "Страховой полис (обязательно с покрытием водного спорта)"),
            ],
            faq=[
                ("item", {
                    "question": "Нужна ли виза?",
                    "answer": (
                        "<p>Да. Виза по прилёту (Visa on Arrival) — 35 USD, "
                        "оплачивается в аэропорту Денпасара в долларах наличными. "
                        "В рублях это около 3 500 ₽ по текущему курсу.</p>"
                    ),
                }),
                ("item", {
                    "question": "Нужна ли страховка?",
                    "answer": (
                        "<p>Обязательно. Медицина на Бали очень дорогая. "
                        "Оформить страховку можно у нас — 9 000 ₽ на весь период. "
                        "Убедитесь, что полис покрывает водный спорт и снорклинг.</p>"
                    ),
                }),
                ("item", {
                    "question": "Можно ли присоединиться одному?",
                    "answer": (
                        "<p>Да. Мы подберём вам соседа по двухместному номеру. "
                        "Если хотите отдельный номер — доплата 60 000 ₽ за тур.</p>"
                    ),
                }),
                ("item", {
                    "question": "Когда лучше ехать?",
                    "answer": (
                        "<p>Март — идеальное время. Начало сухого сезона, "
                        "тёплый океан (+28–29°C), дешёвые авиабилеты и минимум "
                        "туристов по сравнению с пиковым летом. "
                        "Даты тура: 1–14 марта 2027.</p>"
                    ),
                }),
                ("item", {
                    "question": "Гарантированы ли встречи с варанами и акулами?",
                    "answer": (
                        "<p>Мы делаем всё возможное, чтобы вы их увидели — "
                        "но это дикая природа. Компания не несёт ответственности "
                        "за присутствие животных. Верим, что нам повезёт!</p>"
                    ),
                }),
            ],
            cta_heading="Готовы к экспедиции по пяти островам?",
            cta_button="Забронировать место",
            seo_title="Тур-экспедиция: 5 островов Индонезии — Бали, Комодо, Сумбава, Гили | Точка на карте",
            search_description=(
                "14-дневная экспедиция по 5 островам Индонезии: вараны Комодо, "
                "снорклинг с китовыми акулами на Сумбаве, Гили и ритуал Мелукат на Бали. "
                "Группа до 6 человек. Март 2027. От 258 000 ₽."
            ),
        )

        catalog.add_child(instance=tour)
        tour.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"OK Тур создан: {tour.title}"))

        # ── Даты тура ────────────────────────────────────────
        TourDate.objects.create(
            page=tour,
            start_date=datetime.date(2027, 3, 1),
            end_date=datetime.date(2027, 3, 14),
            price=258000,
            currency="RUB",
            total_spots=6,
            spots_left=6,
        )
        self.stdout.write("  OK дата тура: 1–14.03.2027")

        # ── Галерея (вертикальные фото внизу) ───────────────
        captions = {
            "IMG_4790 (2).PNG": "",
            "IMG_8341.HEIC": "Архипелаг Комодо",
            "IMG_8370.HEIC": "Бали",
            "IMG_8381.HEIC": "Индонезия",
            "IMG_9251.HEIC": "",
        }
        for i, img in enumerate(gallery_imgs):
            fname = GALLERY_FILENAMES[i] if i < len(GALLERY_FILENAMES) else ""
            TourGalleryImage.objects.create(
                page=tour,
                image=img,
                caption=captions.get(fname, ""),
                sort_order=i,
            )
        self.stdout.write(f"  OK галерея: {len(gallery_imgs)} фото")

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! Тур доступен по адресу /catalog/{SLUG}/"
        ))
