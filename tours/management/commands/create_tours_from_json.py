"""
python manage.py create_tours_from_json

Импортирует 13 туров из JSON (каталог tours_data) и 4 вьетнамских тура
(каталог tours_data_vietnam) в каталог туров.
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
        "tags": ["Бали", "Индонезия", "Экскурсионный"],
    },
    "bali_komodo": {
        "slug": "bali-komodo",
        "location": "Индонезия · Бали · Комодо",
        "country_tag": "bali",
        "tags": ["Бали", "Индонезия", "Комодо"],
    },
    "bali_java": {
        "slug": "bali-yava-premium",
        "location": "Индонезия · Бали · Ява",
        "country_tag": "bali",
        "tags": ["Бали", "Индонезия", "Ява"],
    },
    "bali-gili": {
        "slug": "sokrovishcha-bali-i-gili",
        "location": "Индонезия · Бали · Гили",
        "country_tag": "bali",
        "tags": ["Бали", "Индонезия", "Гили"],
    },
    "bali-whaleshark": {
        "slug": "bali-i-kitovye-akuly-sumbavy",
        "location": "Индонезия · Бали · Сумбава",
        "country_tag": "bali",
        "tags": ["Бали", "Индонезия", "Сумбава"],
    },
    "bali-shanghai2": {
        "slug": "shankhay-bali-ubud",
        "location": "Китай · Шанхай · Бали · Убуд",
        "country_tag": "bali",
        "tags": ["Бали", "Китай", "Шанхай"],
    },
    "indonesia_malaysia": {
        "slug": "malayziya-i-bali",
        "location": "Малайзия · Бали",
        "country_tag": "bali",
        "tags": ["Малайзия", "Бали", "Премиум"],
    },
    "indonesia_yacht": {
        "slug": "kruiz-sh-minerva",
        "location": "Индонезия · Раджа Ампат",
        "country_tag": "bali",
        "tags": ["Индонезия", "Круиз", "Раджа Ампат"],
        "comfort": "Каюта выбранной категории на борту · All Inclusive",
    },
    "indonesia_shanghai": {
        "slug": "shankhay-bali",
        "location": "Китай · Шанхай · Бали",
        "country_tag": "bali",
        "tags": ["Бали", "Китай", "Шанхай"],
    },
    "papua-bali": {
        "slug": "papua-bali",
        "location": "Индонезия · Папуа · Бали",
        "country_tag": "bali",
        "tags": ["Индонезия", "Папуа", "Бали"],
    },
    "beijing-shanghai": {
        "slug": "pekin-shankhay",
        "location": "Китай · Пекин · Шанхай",
        "country_tag": "china",
        "tags": ["Китай", "Пекин", "Шанхай"],
    },
    "shanghai_bali3": {
        "slug": "shankhay-bali-novyy-god",
        "location": "Китай · Шанхай · Бали",
        "country_tag": "bali",
        "tags": ["Бали", "Китай", "Шанхай"],
    },
    "shanghai_hainan": {
        "slug": "shankhay-haynan-pekin",
        "location": "Китай · Шанхай · Хайнань · Пекин",
        "country_tag": "china",
        "tags": ["Китай", "Шанхай", "Хайнань"],
    },
}

# key из JSON -> настройки вьетнамских туров
VIETNAM_TOURS = {
    "ves-vyetnam": {
        "slug": "ves-vyetnam",
        "location": "Вьетнам · Хошимин · Дананг · Хойан · Ханой · Халонг",
        "country_tag": "vietnam",
        "tags": ["Вьетнам", "Хошимин", "Ханой", "Халонг", "Экскурсионный"],
        "group_size": "групповой · от 1 человека",
    },
    "grand-vyetnam": {
        "slug": "grand-vyetnam",
        "location": "Вьетнам · Хошимин · Дананг · Хуэ · Ханой · Сапа",
        "country_tag": "vietnam",
        "tags": ["Вьетнам", "Хошимин", "Дананг", "Ханой", "Сапа", "Индивидуальный"],
    },
    "fukuok-khoshimin": {
        "slug": "fukuok-khoshimin",
        "location": "Вьетнам · Фукуок · Хошимин",
        "country_tag": "vietnam",
        "tags": ["Вьетнам", "Фукуок", "Хошимин", "Пляжный"],
    },
    "danang-i-sokrovishcha": {
        "slug": "danang-i-sokrovishcha",
        "location": "Вьетнам · Дананг · Хойан · Хуэ",
        "country_tag": "vietnam",
        "tags": ["Вьетнам", "Дананг", "Хойан", "Хуэ"],
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
    help = "Импортирует туры из JSON (Индонезия/Китай + Вьетнам) в каталог."

    def handle(self, *args, **options):
        from tours.models import CatalogPage, TourPage

        datasets = [
            ("Индонезия/Китай", JSON_DIR, PHOTOS_DIR, TOURS, True),
            ("Вьетнам", JSON_DIR_VN, PHOTOS_DIR_VN, VIETNAM_TOURS, False),
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
                if TourPage.objects.filter(slug=cfg["slug"]).exists():
                    skipped.append(cfg["slug"])
                    self.stdout.write(f"Уже существует, пропускаю: {cfg['slug']}")
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
                    summary=data.get("summary", ""),
                    description=text_to_html(data.get("summary", "")),
                    highlights=[("item", h) for h in data.get("highlights", [])],
                    duration=data.get("duration", ""),
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
                tour.save_revision().publish()
                created.append(tour.slug)
                self.stdout.write(self.style.SUCCESS(
                    f"  OK: {tour.slug} — {len(itinerary)} дней, "
                    f"{len(accommodation)} отелей"))

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово. Создано: {len(created)}; пропущено (существующие): {len(skipped)}"))
        for s in created:
            self.stdout.write(f"  /catalog/{s}/")
