"""
python manage.py create_tours_from_json

Импортирует туры из JSON в каталог: 13 туров Индонезия/Китай (tours_data),
4 вьетнамских (tours_data_vietnam) и 3 малайзийских (tours_data_malaysia).
Текст — дословно из источников. Фото — по одному hero на тур.
"""
import os
import re
import io
import json

from django.core.management.base import BaseCommand

JSON_DIR = r"C:\Users\dxmta\AppData\Local\Temp\opencode\tours_data"
PHOTOS_DIR = r"C:\Users\dxmta\AppData\Local\Temp\opencode\tour_photos\final"

JSON_DIR_VN = r"C:\Users\dxmta\AppData\Local\Temp\opencode\tours_data_vietnam"
PHOTOS_DIR_VN = r"C:\Users\dxmta\AppData\Local\Temp\opencode\tour_photos\final_vietnam"

JSON_DIR_MY = r"C:\Users\dxmta\AppData\Local\Temp\opencode\tours_data_malaysia"
PHOTOS_DIR_MY = r"C:\Users\dxmta\AppData\Local\Temp\opencode\tour_photos\final_malaysia"

DEFAULT_GROUP_SIZE = "индивидуально · до 6 человек"
DEFAULT_GROUP_MAX = 6
DEFAULT_COMFORT = "Отели 4–5★ на выбор"
DEFAULT_DIFFICULTY = "Лёгкая"

# key из JSON -> настройки тура
TOURS = {
    "bali_circuit": {
        "slug": "vokrug-bali-za-10-dney",
        "location": "Индонезия · Бали",
        "country_tag": "bali",
        "categories": ["bali"],
        "tags": ["Бали", "Индонезия", "Экскурсионный"],
        "dates": "Любые удобные даты заездов до 31.03.27, исключая периоды 01.07.27-31.08.27 и 20.12.26-15.01.27",
    },
    "bali_komodo": {
        "slug": "bali-komodo",
        "location": "Индонезия · Бали · Комодо",
        "country_tag": "indonesia",
        "categories": ["bali", "indonesia"],
        "tags": ["Бали", "Индонезия", "Комодо"],
        "dates": "Любые даты заездов до 20.12.26",
    },
    "bali_java": {
        "slug": "bali-yava-premium",
        "location": "Индонезия · Бали · Ява",
        "country_tag": "indonesia",
        "categories": ["bali", "indonesia"],
        "tags": ["Бали", "Индонезия", "Ява"],
        "dates": "Любые удобные даты до 20.12.26",
    },
    "bali-gili": {
        "slug": "sokrovishcha-bali-i-gili",
        "location": "Индонезия · Бали · Гили",
        "country_tag": "indonesia",
        "categories": ["bali", "indonesia"],
        "tags": ["Бали", "Индонезия", "Гили"],
        "dates": "Любые даты заездов до 19.12.26",
    },
    "bali-whaleshark": {
        "slug": "bali-i-kitovye-akuly-sumbavy",
        "location": "Индонезия · Бали · Сумбава",
        "country_tag": "indonesia",
        "categories": ["bali", "indonesia"],
        "tags": ["Бали", "Индонезия", "Сумбава"],
        "dates": "Любые даты заездов до 27.03.27. Стоимость на заезды в июле и августе — по запросу.",
    },
    "bali-shanghai2": {
        "slug": "shankhay-bali-ubud",
        "location": "Китай · Шанхай · Бали · Убуд",
        "country_tag": "bali",
        "categories": ["bali", "china"],
        "tags": ["Бали", "Китай", "Шанхай"],
        "dates": "27.12.26 — 04.01.27",
    },
    "indonesia_malaysia": {
        "slug": "malayziya-i-bali",
        "location": "Малайзия · Бали",
        "country_tag": "malaysia",
        "categories": ["malaysia", "bali"],
        "tags": ["Малайзия", "Бали", "Премиум"],
        "dates": "до 26.03.27",
    },
    "indonesia_yacht": {
        "slug": "kruiz-sh-minerva",
        "location": "Индонезия · Раджа Ампат",
        "country_tag": "indonesia",
        "categories": ["indonesia"],
        "tags": ["Индонезия", "Круиз", "Раджа Ампат"],
        "comfort": "Каюта выбранной категории на борту · All Inclusive",
        "dates": "до 15.04.28",
    },
    "indonesia_shanghai": {
        "slug": "shankhay-bali",
        "location": "Китай · Шанхай · Бали",
        "country_tag": "bali",
        "categories": ["bali", "china"],
        "tags": ["Бали", "Китай", "Шанхай"],
        "dates": "Тур индивидуальный, заезды возможны в любую дату до 31.03.27. На 1 заезд нужно не менее 2 человек.",
    },
    "papua-bali": {
        "slug": "papua-bali",
        "location": "Индонезия · Папуа · Бали",
        "country_tag": "indonesia",
        "categories": ["indonesia", "bali"],
        "tags": ["Индонезия", "Папуа", "Бали"],
        "dates": "Любые удобные даты до 18.12.26",
    },
    "beijing-shanghai": {
        "slug": "pekin-shankhay",
        "location": "Китай · Пекин · Шанхай",
        "country_tag": "china",
        "categories": ["china"],
        "tags": ["Китай", "Пекин", "Шанхай"],
        "dates": "24.08.26, 05.09.26, 19.09.26, 12.10.26, 26.10.26, 02.11.26, 23.11.26, 22.02.27, 08.03.27, 05.04.27, 19.04.27, 03.05.27, 24.05.27",
    },
    "shanghai_bali3": {
        "slug": "shankhay-bali-novyy-god",
        "location": "Китай · Шанхай · Бали",
        "country_tag": "bali",
        "categories": ["bali", "china"],
        "tags": ["Бали", "Китай", "Шанхай"],
        "dates": "27.12.26 — 04.01.27",
    },
    "shanghai_hainan": {
        "slug": "shankhay-haynan-pekin",
        "location": "Китай · Шанхай · Хайнань · Пекин",
        "country_tag": "china",
        "categories": ["china"],
        "tags": ["Китай", "Шанхай", "Хайнань"],
        "dates": "до 19.03.27 (пт)",
    },
}

# key из JSON -> настройки малайзийских туров
MALAYSIA_TOURS = {
    "malayziya-singapur": {
        "slug": "malayziya-singapur",
        "location": "Малайзия · Куала-Лумпур · Сингапур",
        "country_tag": "malaysia",
        "categories": ["malaysia"],
        "tags": ["Малайзия", "Сингапур", "Новый год"],
        "group_size": "групповой · от 1 человека",
        "dates": "26.12.26",
        "tour_dates": [
            {"start": "2026-12-26", "end": "2027-01-08", "price": 3623,
             "currency": "USD"},
        ],
    },
    "malayziya-i-bruney": {
        "slug": "malayziya-i-bruney",
        "location": "Малайзия · Бруней · Лангкави",
        "country_tag": "malaysia",
        "categories": ["malaysia"],
        "tags": ["Малайзия", "Бруней", "Лангкави"],
        "group_size": "групповой · от 1 человека",
        "dates": "до 19.03.27",
    },
    "serdtse-borneo": {
        "slug": "serdtse-borneo",
        "location": "Малайзия · Кучинг · Борнео · Дамаи",
        "country_tag": "malaysia",
        "categories": ["malaysia"],
        "tags": ["Малайзия", "Борнео", "Кучинг"],
        "group_size": "групповой · от 1 человека",
        "dates": "до 30.03.27",
    },
}


# key из JSON -> настройки вьетнамских туров
VIETNAM_TOURS = {
    "ves-vyetnam": {
        "slug": "ves-vyetnam",
        "location": "Вьетнам · Хошимин · Дананг · Хойан · Ханой · Халонг",
        "country_tag": "vietnam",
        "categories": ["vietnam"],
        "tags": ["Вьетнам", "Хошимин", "Ханой", "Халонг", "Экскурсионный"],
        "group_size": "групповой · от 1 человека",
        "dates": "Любые даты заездов до 12.12.26. Цены на заезды 30.04.26-02.05.26, 31.08.26-03.09.26, 24.12.26-07.01.27 — по запросу.",
    },
    "grand-vyetnam": {
        "slug": "grand-vyetnam",
        "location": "Вьетнам · Хошимин · Дананг · Хуэ · Ханой · Сапа",
        "country_tag": "vietnam",
        "categories": ["vietnam"],
        "tags": ["Вьетнам", "Хошимин", "Дананг", "Ханой", "Сапа", "Индивидуальный"],
        "dates": "Заезды возможны в удобные даты до 28.11.2026. Нет заездов в периоды: 30.04-02.05, 31.08-03.09.",
    },
    "fukuok-khoshimin": {
        "slug": "fukuok-khoshimin",
        "location": "Вьетнам · Фукуок · Хошимин",
        "country_tag": "vietnam",
        "categories": ["vietnam"],
        "tags": ["Вьетнам", "Фукуок", "Хошимин", "Пляжный"],
        "dates": "Любые даты до 27.12.26",
    },
    "danang-i-sokrovishcha": {
        "slug": "danang-i-sokrovishcha",
        "location": "Вьетнам · Дананг · Хойан · Хуэ",
        "country_tag": "vietnam",
        "categories": ["vietnam"],
        "tags": ["Вьетнам", "Дананг", "Хойан", "Хуэ"],
        "dates": "Без перелёта — любые удобные даты до 03.12.26; с перелётом — вылеты до 21.10.26 по понедельникам, средам и пятницам.",
    },
}


def text_to_html(text):
    """Параграфы (пустая строка) -> <p>, сплошные списки '- ' -> <ul>."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for p in paragraphs:
        lines = [l for l in p.split("\n") if l.strip()]
        if lines and all(re.match(r"^\s*[-*]\s+", l) for l in lines):
            items = "".join(
                f"<li>{re.sub(r'^\s*[-*]\s+', '', l).strip()}</li>" for l in lines
            )
            out.append(f"<ul>{items}</ul>")
        else:
            out.append(f"<p>{' '.join(l.strip() for l in lines)}</p>")
    return "".join(out)


def map_day_number(raw):
    raw = str(raw).strip()
    return "последний" if raw in ("last", "last2") else raw


def parse_hotel(s):
    if ": " in s:
        loc, rest = s.split(": ", 1)
        return rest.strip(), loc.strip()
    return s.strip(), ""


def load_image_file(path):
    from PIL import Image as PILImage
    from PIL import ImageOps
    pil_img = PILImage.open(path)
    try:
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
    help = "Импортирует туры из JSON (Индонезия/Китай + Вьетнам + Малайзия) в каталог."

    def handle(self, *args, **options):
        from tours.models import CatalogPage, TourPage, TourCategory, TourDate

        datasets = [
            ("Индонезия/Китай", JSON_DIR, PHOTOS_DIR, TOURS, True),
            ("Вьетнам", JSON_DIR_VN, PHOTOS_DIR_VN, VIETNAM_TOURS, False),
            ("Малайзия", JSON_DIR_MY, PHOTOS_DIR_MY, MALAYSIA_TOURS, True),
        ]

        catalog = CatalogPage.objects.first()
        if not catalog:
            self.stderr.write("CatalogPage не найдена.")
            return

        created, skipped = [], []
        for label, json_dir, photos_dir, cfg_map, underscore in datasets:
            self.stdout.write(f"\n=== {label} ===")
            for fname in sorted(os.listdir(json_dir)):
                if not fname.endswith(".json"):
                    continue
                fpath = os.path.join(json_dir, fname)
                data = json.load(open(fpath, encoding="utf-8"))
                key = data.get("key")
                cfg = cfg_map.get(key)
                if not cfg:
                    self.stderr.write(f"Нет конфигурации для ключа: {key}")
                    continue
                existing = TourPage.objects.filter(slug=cfg["slug"]).first()
                if existing:
                    changed = []
                    if cfg.get("dates") and existing.dates_info != cfg["dates"]:
                        existing.dates_info = cfg["dates"]
                        changed.append("даты")
                    want_codes = cfg.get("categories") or [cfg["country_tag"]]
                    have_codes = list(existing.categories.values_list("code", flat=True))
                    if sorted(want_codes) != sorted(have_codes):
                        existing.categories.set(
                            TourCategory.objects.filter(code__in=want_codes))
                        changed.append("категории")
                    want_dates = cfg.get("tour_dates") or []
                    if want_dates and not existing.tour_dates.exists():
                        for td in want_dates:
                            TourDate.objects.create(
                                page=existing,
                                start_date=td["start"], end_date=td["end"],
                                price=td["price"], currency=td.get("currency", "RUB"))
                        changed.append("даты заездов")
                    if changed:
                        existing.save_revision().publish()
                        self.stdout.write(
                            f"Обновил ({', '.join(changed)}): {cfg['slug']}")
                    else:
                        self.stdout.write(f"Уже существует, пропускаю: {cfg['slug']}")
                    skipped.append(cfg["slug"])
                    continue

                self.stdout.write(f"Создаю: {data['title']}")

                photo_name = key.replace('-', '_') if underscore else key
                photo_path = os.path.join(photos_dir, f"{photo_name}.jpg")
                if not os.path.exists(photo_path):
                    self.stderr.write(f"  Нет hero-фото: {photo_path}")
                    continue

                hero = upload_wagtail_image(
                    f"Тур «{data['title']}» — обложка",
                    load_image_file(photo_path),
                    f"{key}.jpg",
                )

                itinerary = []
                for d in data.get("days", []):
                    itinerary.append(("day", {
                        "day_number": map_day_number(d.get("day", "")),
                        "title": d.get("title", ""),
                        "description": text_to_html(d.get("description", "")),
                    }))

                accommodation = []
                for h in data.get("hotels", []):
                    name, htype = parse_hotel(h)
                    accommodation.append(("item", {
                        "name": name,
                        "type": htype,
                        "description": "",
                        "image": None,
                    }))

                tour = TourPage(
                    title=data["title"],
                    slug=cfg["slug"],
                    location=cfg["location"],
                    summary="",
                    description=text_to_html(data.get("summary", "")),
                    highlights=[("item", h) for h in data.get("highlights", [])],
                    duration=data.get("duration", ""),
                    dates_info=cfg.get("dates", ""),
                    group_size=cfg.get("group_size", DEFAULT_GROUP_SIZE),
                    group_size_max=cfg.get("group_size_max", DEFAULT_GROUP_MAX),
                    comfort=cfg.get("comfort", DEFAULT_COMFORT),
                    difficulty=cfg.get("difficulty", DEFAULT_DIFFICULTY),
                    price_from=data.get("price_short", ""),
                    country_tag=cfg["country_tag"],
                    hero_images=[("image", hero)],
                    itinerary=itinerary,
                    accommodation=accommodation,
                    included=[("item", x) for x in data.get("included", [])],
                    excluded=[("item", x) for x in data.get("excluded", [])],
                )

                catalog.add_child(instance=tour)
                tour.tags.add(*cfg["tags"])
                tour.categories.set(
                    TourCategory.objects.filter(
                        code__in=cfg.get("categories") or [cfg["country_tag"]]))
                tour.save_revision().publish()
                for td in cfg.get("tour_dates") or []:
                    TourDate.objects.create(
                        page=tour,
                        start_date=td["start"], end_date=td["end"],
                        price=td["price"], currency=td.get("currency", "RUB"))
                created.append(tour.slug)
                self.stdout.write(self.style.SUCCESS(
                    f"  OK: {tour.slug} — {len(itinerary)} дней, "
                    f"{len(accommodation)} отелей"))

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово. Создано: {len(created)}; пропущено (существующие): {len(skipped)}"))
        for s in created:
            self.stdout.write(f"  /catalog/{s}/")
