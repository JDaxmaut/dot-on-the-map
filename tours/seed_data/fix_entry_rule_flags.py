import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tochka.settings")
django.setup()

from wagtail.images import get_image_model

from tours.models import EntryRuleCountryPage

COUNTRY_TO_ISO = {
    "vietnam": "vn",
    "indonesia": "id",
    "china": "cn",
    "cambodia": "kh",
    "japan": "jp",
    "laos": "la",
    "malaysia": "my",
    "nepal": "np",
    "philippines": "ph",
    "thailand": "th",
    "korea": "kr",
}

Image = get_image_model()

fixed = []
for page in EntryRuleCountryPage.objects.live():
    iso = COUNTRY_TO_ISO.get(page.country_code)
    if not iso:
        continue
    path = f"original_images/flag-{iso}.png"
    image = page.flag_image
    if image is None:
        image = Image(title=f"Флаг {page.title}", file=path, file_hash="", width=256, height=192)
    else:
        image.file = path
        image.file_hash = ""
        image.width = 256
        image.height = 192
        image.title = f"Флаг {page.title}"
    image.save()
    page.flag_image = image
    page.save()
    rev = page.save_revision()
    rev.publish()
    fixed.append(page.country_code)

print("OK: fixed flags for", ", ".join(fixed))
