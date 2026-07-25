import os
import re
from django.core.management.base import BaseCommand
from django.core.files import File
from wagtail.models import Page, Collection
from wagtail.images.models import Image
from tours.models import EntryRulesIndexPage, EntryRuleCountryPage


COUNTRY_DATA = {
    "vietnam": {
        "title": "Вьетнам",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "45 дней (eVisa), до 90 дней по продлению",
    },
    "indonesia": {
        "title": "Индонезия",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (безвизовый), можно продлить",
    },
    "china": {
        "title": "Китай",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": True,
        "max_stay": "До 90 дней по туристической визе",
    },
    "cambodia": {
        "title": "Камбоджа",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (eVisa/VOA)",
    },
    "japan": {
        "title": "Япония",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": True,
        "max_stay": "До 90 дней по туристической визе",
    },
    "laos": {
        "title": "Лаос",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (VOA/eVisa)",
    },
    "malaysia": {
        "title": "Малайзия",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "До 90 дней без визы",
    },
    "nepal": {
        "title": "Непал",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "15/30/90 дней (VOA/eVisa)",
    },
    "philippines": {
        "title": "Филиппины",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "До 30 дней без визы",
    },
    "thailand": {
        "title": "Таиланд",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "60 дней без визы (с 01.05.2024)",
    },
    "korea": {
        "title": "Южная Корея",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": True,
        "max_stay": "До 90 дней (K-ETA или виза)",
    },
}


def indent(line):
    return len(line) - len(line.lstrip())


def stripped(line):
    return line.strip()


def parse_notes(text):
    lines = text.split("\n")
    result = []
    i = 0

    def is_bullet(s):
        return s.startswith("- ") or s.startswith("• ") or s.startswith("* ")

    def has_ordered_prefix(s):
        return bool(re.match(r"^\d+[\.\)]\s", s))

    def strip_bullet(s):
        if s.startswith("- ") or s.startswith("• ") or s.startswith("* "):
            return s[2:]
        m = re.match(r"^\d+[\.\)]\s", s)
        if m:
            return s[m.end():]
        return s

    def is_header_line(s, next_indent):
        if not s or s.startswith("<"):
            return False
        if is_bullet(s) or has_ordered_prefix(s):
            return False
        if next_indent >= 2:
            return True
        if len(s) < 50 and not s.endswith("."):
            return True
        if s.endswith(":") and len(s) < 70:
            return True
        return False

    while i < len(lines):
        line = lines[i]
        s = stripped(line)
        lev = indent(line)

        if not s:
            i += 1
            continue

        if s.startswith("<"):
            result.append(s)
            i += 1
            continue

        next_non_blank = None
        for j in range(i + 1, len(lines)):
            if stripped(lines[j]):
                next_non_blank = (stripped(lines[j]), indent(lines[j]))
                break

        if lev == 0 and is_header_line(s, next_non_blank[1] if next_non_blank else 0):
            if s.endswith(":") and next_non_blank and next_non_blank[1] >= 2:
                if len(s) > 15:
                    result.append(f"<h3>{s}</h3>")
                else:
                    result.append(f"<h2>{s}</h2>")
            elif len(s) < 50:
                result.append(f"<h2>{s}</h2>")
            else:
                result.append(f"<h2>{s}</h2>")
            i += 1
            continue

        if lev >= 2 or is_bullet(s) or has_ordered_prefix(s):
            items = []
            while i < len(lines):
                l = lines[i]
                ss = stripped(l)
                ll = indent(l)
                if not ss:
                    i += 1
                    continue
                if ll < 2 and not is_bullet(ss) and not has_ordered_prefix(ss):
                    break
                items.append(ss)
                i += 1
            if items:
                is_ordered = has_ordered_prefix(items[0])
                tag = "ol" if is_ordered else "ul"
                lis = "\n".join(f"  <li>{strip_bullet(it)}</li>" for it in items)
                result.append(f"<{tag}>\n{lis}\n</{tag}>")
            continue

        paras = [s]
        i += 1
        while i < len(lines):
            l = lines[i]
            ss = stripped(l)
            if not ss:
                i += 1
                break
            ll = indent(l)
            if ll == 0 and (is_header_line(ss, indent(lines[i + 1]) if i + 1 < len(lines) else 0) or is_bullet(ss) or has_ordered_prefix(ss) or ll >= 2):
                break
            if ll >= 2:
                break
            paras.append(ss)
            i += 1
        if paras:
            para_text = " ".join(paras)
            result.append(f"<p>{para_text}</p>")

    return "\n".join(result)


FLAG_FILES = {
    "vietnam": "vietnam(pics.1).jpg",
    "indonesia": "indonesia-2(pics.3).jpg",
    "china": "China(pics.1).jpg",
    "cambodia": "Cambodia(pics.1).jpg",
    "japan": "japan-2(pics.2).jpg",
    "laos": "laos(pics.1).jpg",
    "malaysia": "malaysia-2(pics.2).jpg",
    "nepal": "nepa-2l(pics.2).jpg",
    "philippines": "philippines-2(pics.2).jpg",
    "thailand": "thailand-2(pics.2).jpg",
    "korea": "south-korea-2(pics.1).jpg",
}


def upload_flag(code, page, seed_dir, collection):
    fname = FLAG_FILES.get(code)
    if not fname:
        return False
    fpath = os.path.join(seed_dir, fname)
    if not os.path.exists(fpath):
        return False
    with open(fpath, "rb") as f:
        image = Image(
            title=f"flag-{code}",
            file=File(f, name=f"flag-{code}.jpg"),
            collection=collection,
        )
        image.save()
    page.flag_image = image
    return True


class Command(BaseCommand):
    help = "Создание/обновление всех страниц Правила въезда на продакшене"

    def handle(self, *args, **options):
        self.stdout.write("Создание/проверка страниц Правила въезда...")

        # 1. Create or get EntryRulesIndexPage
        home = Page.objects.get(slug="home")
        index = EntryRulesIndexPage.objects.first()

        if not index:
            index = EntryRulesIndexPage(
                title="Правила въезда",
                slug="entry-rules",
                intro=(
                    "<p>Актуальные правила въезда для популярных стран Азии. "
                    "Информация обновляется регулярно.</p>"
                ),
            )
            home.add_child(instance=index)
            index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  Создана страница Правила въезда"))
        else:
            self.stdout.write("  Страница Правила въезда уже существует")

        # 2. Get or create flags collection
        root = Collection.get_first_root_node()
        flags_collection = root.get_children().filter(name="Флаги стран").first()
        if not flags_collection:
            flags_collection = root.add_child(name="Флаги стран")

        # 3. Create/update country pages
        seed_dir = os.path.join(os.path.dirname(__file__), "..", "..", "seed_data")

        country_notes = {}
        for fname in os.listdir(seed_dir):
            if not fname.endswith(".txt"):
                continue
            fpath = os.path.join(seed_dir, fname)
            name = fname.rsplit(".", 1)[0].lower()
            code = {"nepa": "nepal", "south-korea": "korea"}.get(name, name.replace("-", ""))
            with open(fpath, "r", encoding="utf-8") as f:
                country_notes[code] = f.read().strip()

        for code, data in COUNTRY_DATA.items():
            page = EntryRuleCountryPage.objects.filter(country_code=code).first()

            if page:
                updated = False
                if not page.notes:
                    raw = country_notes.get(code, "")
                    if raw and not raw.startswith("<"):
                        page.notes = parse_notes(raw)
                    elif raw:
                        page.notes = raw
                    updated = True
                if not page.flag_image:
                    if upload_flag(code, page, seed_dir, flags_collection):
                        updated = True
                        self.stdout.write(f"  {data['title']}: добавлен флаг")
                if updated:
                    page.save_revision().publish()
                    self.stdout.write(f"  {data['title']}: обновлено")
                else:
                    self.stdout.write(f"  {data['title']}: уже существует")
                continue

            page = EntryRuleCountryPage(
                title=data["title"],
                slug=code,
                country_code=code,
                visa_free=data["visa_free"],
                visa_on_arrival=data["visa_on_arrival"],
                e_visa=data["e_visa"],
                visa_required=data["visa_required"],
                max_stay=data["max_stay"],
            )

            # Set notes
            raw_notes = country_notes.get(code, "")
            if raw_notes and not raw_notes.startswith("<"):
                page.notes = parse_notes(raw_notes)
            else:
                page.notes = raw_notes

            upload_flag(code, page, seed_dir, flags_collection)

            index.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  Создана: {data['title']}"))

        self.stdout.write(self.style.SUCCESS("Готово!"))