import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tochka.settings")
django.setup()

from tours.models import AboutPage

about = AboutPage.objects.first()

about.registry_number = "РТА 0054495"
about.is_operator = False

about.save()
rev = about.save_revision()
rev.publish()
print("OK: about page registry number set")
