"""
python manage.py create_tour_hotels_vietnam

Создаёт тур «Вьетнам с надёжным принимающим туроператором»:
Дананг · Нячанг · Фукуок. 32 отеля 4–5★ на выбор, даты и цена — по запросу.
"""
import os
import io

from django.core.management.base import BaseCommand


SLUG = "vietnam-s-nadezhnym-prinimayushchim-turoperatorom"

PHOTOS_TOUR = r"C:\Users\dxmta\Desktop\biba\фото тура"
HOTELS_BASE = r"C:\Users\dxmta\Desktop\biba"

HERO_FILENAMES = [
    "pexels-haneul-trac-246343735-38720555.jpg",
    "pexels-quang-nguyen-vinh-222549-6346639.jpg",
    "pexels-quang-nguyen-vinh-222549-6875008.jpg",
    "pexels-wanderarch-18893625.jpg",
    "pexels-yukophotography-36636305.jpg",
]

GALLERY_FILENAMES = [
    "pexels-hducdev-17111168 (2).jpg",
    "pexels-hoa-le-dinh-1615807371-28448335 (2).jpg",
    "pexels-kirandeepsingh-20539372.jpg",
    "pexels-lurk-207144614-15694533.jpg",
    "pexels-natalia-23512369-6769701 (2).jpg",
    "pexels-nguy-n-huy-1091648355-20656446 (2).jpg",
    "pexels-nguy-n-thanh-ng-c-485749-3995670.jpg",
    "pexels-petra-nesti-1766376-31187735 (2).jpg",
    "pexels-quang-nguyen-vinh-222549-26742979 (2).jpg",
    "pexels-ti-u-b-o-tr-ng-41366219-7336586.jpg",
]

# фото для дней маршрута: (имя файла, подпись)
DAY_IMAGES = [
    ("pexels-nguyndoanfoto-31038748.jpg", "Пляж Микхе, Дананг"),
    ("pexels-phat-tr-ng-1662052981-38695397.jpg", "Горы Ба На и Золотой мост"),
    ("pexels-tomas-malik-793526-1660996.jpg", "Старый город Хойана"),
    ("pexels-pragyanbezbo-26550066.jpg", "Залив Нячанга"),
    ("pexels-wlamnv-37800653.jpg", "Острова Нячанга"),
    ("pexels-vo-van-ti-n-2037497312-38806321.jpg", "Пляж Кем, Фукуок"),
    ("pexels-quang-nguyen-vinh-222549-2134272 (2).jpg", "Канатная дорога Хонтхом"),
    ("pexels-tuan-vy-903011268-32843809.jpg", "Закат над морем"),
]

# отели: {название_папки: (город, [ (файл, звёзды, описание), ... ])}
HOTELS = {
    "отели дананг": (
        "Дананг",
        [
            ("Crowne Plaza Danang Hotel & Resort.jpg", 4,
             "Крупный пляжный отель сети IHG на берегу залива Дананг, собственный пляж и несколько бассейнов."),
            ("Four Points by Sheraton Danang.jpg", 4,
             "Современный отель сети Marriott с панорамным видом на море и бассейном на крыше."),
            ("Grandvrio Ocean Resort Danang.jpg", 4,
             "Пляжный резорт с японским вниманием к деталям, прямо у воды."),
            ("InterContinental Danang Sun Peninsula Resort, an IHG Hotel.jpg", 5,
             "Легендарный резорт Билла Бенсли на полуострове Сон Тра — один из лучших в мире."),
            ("KOI Resort & Residence Da Nang.jpg", 5,
             "Резорт-комплекс с виллами в зелёной части Дананга, спа и открытые бассейны."),
            ("Renaissance Hoi An Resort & Spa.jpg", 5,
             "Резорт сети Marriott в Хойане с видом на реку Тху Бон и пляж."),
            ("Sheraton Grand Danang Resort.jpg", 5,
             "Роскошный пляжный резорт с большим спа-центром и ресторанами на берегу."),
            ("Shilla Monogram Quangnam Danang.jpg", 5,
             "Бутик-отель корейской сети Shilla между Данангом и Хойаном."),
            ("Vinpearl Resort & Golf Nam Hoi An.jpg", 5,
             "Резорт Vinpearl с полем для гольфа, аквапарком и собственным пляжем."),
            ("Wyndham Hoi An Royal Beachfront Resort & Villas.jpg", 5,
             "Отель Wyndham с видом на пляж и реку, виллы с бассейнами."),
        ],
    ),
    "отели нячанг": (
        "Нячанг",
        [
            ("An Vista Hotel.jpg", 5,
             "Высокий отель у пляжа Нячанга с панорамным видом на залив."),
            ("Cam Ranh Riviera.jpg", 4,
             "Резорт на полуострове Камрань с собственной лагуной и песчаным пляжем."),
            ("December Hotel.jpg", 4,
             "Уютный отель в центре Нячанга, в паре минут от пляжа."),
            ("DTX Hotel Nha Trang.jpg", 4,
             "Современный отель с бассейном на крыше и видом на море."),
            ("GRAND GOSIA HOTEL 4.jpg", 4,
             "Отель с панорамным рестораном и бассейном на верхнем этаже."),
            ("Queen Ann Nha Trang Hotel.jpg", 5,
             "Высокий отель с видом на море в центре курорта."),
            ("Seana Hotel.jpg", 4,
             "Бутик-отель с террасой у пляжа Нячанга."),
            ("Selectum Noa Resort.jpg", 5,
             "Пляжный резорт с большой территорией, бассейнами и спа."),
            ("Vesna Hotel.jpg", 4,
             "Комфортный отель у пляжа с бассейном и рестораном."),
            ("VINPEARL RESORT NHA TRANG 5.jpg", 5,
             "Легендарный резорт Vinpearl на острове Хон Че, соединён канатной дорогой с городом."),
            ("Virgo Hotel Nha Trang.jpg", 4,
             "Отель с видом на море в центре Нячанга."),
        ],
    ),
    "отели фукок": (
        "Фукуок",
        [
            ("Amarin Resort & Spa Phu Quoc.jpg", 4,
             "Тропический резорт со спа-центром на юге Фукуока."),
            ("Crowne Plaza Phu Quoc Starbay.jpg", 5,
             "Большой пляжный отель IHG на западном побережье острова."),
            ("Dusit Princess Moonrise Beach Resort.jpg", 4,
             "Резорт тайской сети Dusit с частным пляжем."),
            ("Melia Vinpearl Phu Quoc 5.jpg", 5,
             "Резорт Meliá на пляже Кем — одном из самых красивых на острове."),
            ("Paralia Phu Quoc Khem Beach 3.jpg", 3,
             "Уютный отель прямо у пляжа Кем на юге острова."),
            ("Premier Residences Phu Quoc Emerald Bay 5.jpg", 5,
             "Апарт-резорт сети Marriott на пляже Кем."),
            ("Sol By Melia Phu Quoc.jpg", 4,
             "Жизнерадостный пляжный отель сети Meliá с развлечениями."),
            ("Vinpearl Resort & Spa Phu Quoc 5.jpg", 5,
             "Крупнейший резорт Vinpearl с собственным пляжем и парком."),
            ("Vinpearl Wonderworld PQ 5.jpg", 5,
             "Парковый резорт Vinpearl рядом с аквапарком и зоопарком."),
            ("WYNDHAM GARDEN GRANDWORLD PHU QUOC 4.jpg", 4,
             "Отель в туристическом комплексе Грандворлд с ресторанами и магазинами рядом."),
            ("WYNDHAM GRAND PHU QUOC 5.jpg", 5,
             "Роскошный пляжный отель Wyndham на северном побережье острова."),
        ],
    ),
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
    help = "Создаёт тур «Вьетнам с надёжным принимающим туроператором» (Дананг · Нячанг · Фукуок)."

    def add_arguments(self, parser):
        parser.add_argument("--photos", default=PHOTOS_TOUR,
                            help="Путь к папке с фотографиями тура")
        parser.add_argument("--hotels", default=HOTELS_BASE,
                            help="Путь к папке с фото отелей")

    def handle(self, *args, **options):
        from tours.models import CatalogPage, TourPage, TourGalleryImage

        if TourPage.objects.filter(slug=SLUG).exists():
            self.stdout.write(f"Тур уже существует: {SLUG}")
            return

        catalog = CatalogPage.objects.first()
        if not catalog:
            self.stderr.write("CatalogPage не найдена.")
            return

        photos_dir = options["photos"]
        hotels_dir = options["hotels"]

        self.stdout.write("Загружаю фото тура…")

        hero_images = []
        for fname in HERO_FILENAMES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю: {fname}")
                continue
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(
                    f"Отели Вьетнама — hero — {fname}", data, f"oteli_vn_hero_{fname}.jpg")
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
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(
                    f"Отели Вьетнама — галерея — {fname}", data, f"oteli_vn_gallery_{fname}.jpg")
                gallery_imgs.append(img)
                self.stdout.write(f"  OK gallery: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        day_imgs = {}
        for fname, caption in DAY_IMAGES:
            fpath = os.path.join(photos_dir, fname)
            if not os.path.exists(fpath):
                self.stdout.write(f"  Пропускаю день-фото: {fname}")
                continue
            try:
                data = load_image_file(fpath)
                img = upload_wagtail_image(
                    f"Отели Вьетнама — день — {fname}", data, f"oteli_vn_day_{fname}.jpg")
                day_imgs[fname] = img
                self.stdout.write(f"  OK day: {fname} ->id={img.pk}")
            except Exception as e:
                self.stdout.write(f"  Ошибка {fname}: {e}")

        self.stdout.write("Загружаю фото отелей…")

        accommodation = []
        for folder, (city, hotels) in HOTELS.items():
            folder_path = os.path.join(hotels_dir, folder)
            for fname, stars, desc in hotels:
                fpath = os.path.join(folder_path, fname)
                if not os.path.exists(fpath):
                    self.stdout.write(f"  Пропускаю отель: {fname}")
                    continue
                try:
                    data = load_image_file(fpath)
                    name = os.path.splitext(fname)[0]
                    title = f"Отель {city} — {name}"
                    img = upload_wagtail_image(
                        title, data, f"oteli_vn_hotel_{city}_{fname}.jpg")
                    accommodation.append(("item", {
                        "name": name,
                        "type": f"{city} · отель {stars}★",
                        "description": desc,
                        "image": img,
                    }))
                    self.stdout.write(f"  OK отель: {name} ->id={img.pk}")
                except Exception as e:
                    self.stdout.write(f"  Ошибка {fname}: {e}")

        self.stdout.write("Создаю страницу тура…")

        def day_photo(fname):
            return day_imgs.get(fname)

        itinerary = [
            ("day", {
                "day_number": "1",
                "title": "Прилёт в Дананг",
                "description": (
                    "<p>Трансфер из аэропорта, заселение в выбранный отель. "
                    "Первый вечер — прогулка по пляжу Микхе и ужин с морепродуктами.</p>"
                ),
                "image": day_photo("pexels-nguyndoanfoto-31038748.jpg"),
            }),
            ("day", {
                "day_number": "2",
                "title": "Дананг: горы Ба На",
                "description": (
                    "<p>Подъём по одной из самых длинных канатных дорог в мире, "
                    "Золотой мост в руках великана, французская деревня и смотровые площадки.</p>"
                ),
                "image": day_photo("pexels-phat-tr-ng-1662052981-38695397.jpg"),
            }),
            ("day", {
                "day_number": "3",
                "title": "Хойан — город фонарей",
                "description": (
                    "<p>Переезд в Хойан: старый город под охраной ЮНЕСКО, вечерняя "
                    "процессия фонарей и мастер-класс по вьетнамской кухне.</p>"
                ),
                "image": day_photo("pexels-tomas-malik-793526-1660996.jpg"),
            }),
            ("day", {
                "day_number": "4",
                "title": "Перелёт в Нячанг",
                "description": (
                    "<p>Внутренний перелёт на юг, заселение в отель у моря и "
                    "отдых после насыщенных дней.</p>"
                ),
                "image": day_photo("pexels-pragyanbezbo-26550066.jpg"),
            }),
            ("day", {
                "day_number": "5",
                "title": "Острова Нячанга",
                "description": (
                    "<p>Морская прогулка по заливу: снорклинг у коралловых рифов, "
                    "обед на острове и купание в лазурной воде.</p>"
                ),
                "image": day_photo("pexels-wlamnv-37800653.jpg"),
            }),
            ("day", {
                "day_number": "6",
                "title": "Перелёт на Фукуок",
                "description": (
                    "<p>Перелёт на остров, заселение в пляжный резорт и первый закат "
                    "на побережье Сиамского залива.</p>"
                ),
                "image": day_photo("pexels-vo-van-ti-n-2037497312-38806321.jpg"),
            }),
            ("day", {
                "day_number": "7",
                "title": "Фукуок: пляж и Хонтхом",
                "description": (
                    "<p>День на пляже Кем и подъём на канатной дороге Хонтхом — "
                    "самой длинной в мире. Вечером — ночной рынок Динь Кау.</p>"
                ),
                "image": day_photo("pexels-quang-nguyen-vinh-222549-2134272 (2).jpg"),
            }),
            ("day", {
                "day_number": "8",
                "title": "Спа и выезд",
                "description": (
                    "<p>Свободный день: спа у моря, последние прогулки. "
                    "Трансфер в аэропорт и вылет домой.</p>"
                ),
                "image": day_photo("pexels-tuan-vy-903011268-32843809.jpg"),
            }),
        ]

        tour = TourPage(
            title="Вьетнам с надёжным принимающим туроператором",
            slug=SLUG,
            location="Вьетнам · Дананг · Нячанг · Фукуок",
            summary=(
                "Отельный тур по трём курортам Вьетнама — Дананг, Нячанг и Фукуок — "
                "с надёжным принимающим туроператором. 32 отеля 4–5★ на выбор, "
                "индивидуальная сборка, даты — любые, по запросу."
            ),
            description=(
                "<p>Большой отельный тур по трём пляжным курортам Вьетнама — Дананг, "
                "Нячанг и Фукуок. В подборке 32 отеля 4–5★: от уютных городских "
                "бутик-отелей до легендарных пляжных резортов мировых сетей.</p>"
                "<p><strong>Как это работает:</strong></p>"
                "<ul>"
                "<li>выбираете один или несколько курортов — Дананг, Нячанг, Фукуок;</li>"
                "<li>выбираете отель из подборки (или просите нас подобрать);</li>"
                "<li>называете удобные даты и длительность поездки;</li>"
                "<li>мы собираем тур: отели, трансферы, перелёты между курортами и экскурсии.</li>"
                "</ul>"
                "<p>Даты заездов — любые, по запросу: тур стартует в удобное для вас время. "
                "Стоимость рассчитывается индивидуально под выбранные отель, даты и "
                "продолжительность. Программа ниже — пример комбинированного маршрута "
                "по трём курортам; её можно сократить до одного курорта или продлить.</p>"
            ),
            highlights=[
                ("item", "Надёжный принимающий туроператор во Вьетнаме"),
                ("item", "32 отеля 4–5★ в одной подборке"),
                ("item", "Три курорта: Дананг, Нячанг, Фукуок"),
                ("item", "Даты заездов — любые, по запросу"),
                ("item", "Индивидуальная сборка под ваши планы"),
                ("item", "Внутренние перелёты между курортами"),
                ("item", "Русскоязычная поддержка на всём пути"),
            ],
            duration="7–14 дней / на выбор",
            group_size="индивидуально · до 6 человек",
            group_size_max=6,
            comfort="Отели 4–5★ на выбор",
            difficulty="Лёгкая",
            price_from="Цена по запросу",
            country_tag="vietnam",
            hero_images=[("image", img) for img in hero_images],
            itinerary=itinerary,
            accommodation=accommodation,
            included=[
                ("item", "Проживание в выбранном отеле на завтраках"),
                ("item", "Трансферы из/в аэропорт по программе"),
                ("item", "Внутренние перелёты между курортами"),
                ("item", "Подбор отеля и сборка тура под ваши пожелания"),
                ("item", "Русскоязычная поддержка 24/7"),
                ("item", "Медицинская страховка"),
            ],
            excluded=[
                ("item", "Международный перелёт"),
                ("item", "Обеды и ужины (кроме указанных)"),
                ("item", "Экскурсии и дополнительные услуги отеля"),
                ("item", "Личные расходы и чаевые"),
            ],
            cancel_policy=[
                ("item", {
                    "period": "За 30+ дней",
                    "description": "Полный возврат стоимости тура",
                    "refund_percent": 100,
                }),
                ("item", {
                    "period": "14–29 дней",
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
                "возврат 100% независимо от срока."
            ),
            what_to_bring=[
                ("item", "Загранпаспорт (срок действия минимум 6 месяцев)"),
                ("item", "Лёгкая одежда и купальники"),
                ("item", "Солнцезащитный крем"),
                ("item", "Удобная обувь для экскурсий"),
                ("item", "Наличные (доллары и донги)"),
                ("item", "Страховой полис"),
            ],
            faq=[
                ("item", {
                    "question": "Какие даты заездов?",
                    "answer": "<p>Тур стартует в любые удобные для вас даты — по запросу. "
                              "Напишите нам, и мы подберём отель и заезд.</p>",
                }),
                ("item", {
                    "question": "Сколько стоит тур?",
                    "answer": "<p>Стоимость зависит от выбранного курорта, отеля и "
                              "длительности поездки. Оставьте заявку — рассчитаем "
                              "индивидуально под ваш бюджет.</p>",
                }),
                ("item", {
                    "question": "Нужно ли ехать на все три курорта?",
                    "answer": "<p>Нет. Можно остановиться на одном курорте или "
                              "скомбинировать несколько — как вам удобнее.</p>",
                }),
                ("item", {
                    "question": "Как выбрать отель?",
                    "answer": "<p>В подборке 32 отеля 4–5★ в Дананге, Нячанге и Фукуоке. "
                              "Мы поможем выбрать под ваши пожелания и бюджет.</p>",
                }),
                ("item", {
                    "question": "Включён ли перелёт?",
                    "answer": "<p>Международный перелёт бронируется отдельно. Внутренние "
                              "перелёты между курортами мы организуем.</p>",
                }),
            ],
            cta_heading="Выберите свой идеальный отель во Вьетнаме",
            cta_button="Подобрать тур",
            seo_title=(
                "Вьетнам с надёжным туроператором: отели Дананга, Нячанга и Фукуока "
                "| Точка на карте"
            ),
            search_description=(
                "Отельный тур по Вьетнаму: 32 отеля 4–5★ в Дананге, Нячанге и Фукуоке. "
                "Индивидуальная сборка, даты — по запросу."
            ),
        )

        catalog.add_child(instance=tour)
        tour.tags.add("Вьетнам", "Отели", "Пляж")
        tour.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"OK Тур создан: {tour.title}"))

        for i, img in enumerate(gallery_imgs):
            TourGalleryImage.objects.create(
                page=tour, image=img, caption="", sort_order=i,
            )
        self.stdout.write(f"  OK галерея: {len(gallery_imgs)} фото")

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! /catalog/{SLUG}/"
        ))
