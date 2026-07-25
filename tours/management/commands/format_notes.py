import re
from django.core.management.base import BaseCommand
from tours.models import EntryRuleCountryPage


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

        # Already HTML
        if s.startswith("<"):
            result.append(s)
            i += 1
            continue

        # Look ahead to determine if this is a header
        next_non_blank = None
        for j in range(i + 1, len(lines)):
            if stripped(lines[j]):
                next_non_blank = (stripped(lines[j]), indent(lines[j]))
                break

        # Header detection
        if lev == 0 and is_header_line(s, next_non_blank[1] if next_non_blank else 0):
            if s.endswith(":") and next_non_blank and next_non_blank[1] >= 2:
                # Could be h3 if followed by content
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

        # List items: group consecutive items
        if lev >= 2 or is_bullet(s) or has_ordered_prefix(s):
            items = []
            while i < len(lines):
                l = lines[i]
                ss = stripped(l)
                ll = indent(l)

                if not ss:
                    # Skip blank lines within list
                    i += 1
                    continue

                if ll < 2 and not is_bullet(ss) and not has_ordered_prefix(ss):
                    # Indent dropped -> end of list
                    # But check if next non-blank after this is indented again
                    break

                items.append(ss)
                i += 1

            if items:
                is_ordered = has_ordered_prefix(items[0])
                tag = "ol" if is_ordered else "ul"
                lis = "\n".join(f"  <li>{strip_bullet(it)}</li>" for it in items)
                result.append(f"<{tag}>\n{lis}\n</{tag}>")
            continue

        # Regular paragraph(s) - group consecutive lines
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


class Command(BaseCommand):
    help = "Форматирование заметок в RichText"

    def handle(self, *args, **options):
        pages = EntryRuleCountryPage.objects.all()
        updated = 0

        for page in pages:
            raw = page.notes or ""
            if not raw.strip():
                self.stdout.write(f"  {page.country_code}: пусто")
                continue

            if raw.strip().startswith("<"):
                self.stdout.write(f"  {page.country_code}: уже HTML")
                continue

            formatted = parse_notes(raw)

            if formatted == raw:
                self.stdout.write(f"  {page.country_code}: без изменений")
                continue

            page.notes = formatted
            revision = page.save_revision()
            revision.publish()
            self.stdout.write(self.style.SUCCESS(f"  {page.country_code}: отформатирован"))
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Готово! Отформатировано {updated}"))