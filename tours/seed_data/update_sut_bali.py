import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tochka.settings")
django.setup()

from tours.models import TourPage

tour = TourPage.objects.get(slug="sut-bali")

tour.included = [
    ("item", "Проживание в 2-х местных номерах в отелях или виллах. Будет зависеть от количества человек в группе."),
    ("item", "Завтраки на протяжении всего тура"),
    ("item", "Трансфер по программе — все местные переезды"),
    ("item", "Встреча в аэропорту и проводы на вылет"),
    ("item", "Сопровождение гидом все 14 дней тура"),
]

tour.accommodation = [
    ("item", {
        "name": "Bintang Bali Resort",
        "type": "Отель",
        "description": "Курортный отель с бассейнами и выходом к пляжу.",
        "image": None,
    }),
    ("item", {
        "name": "Truntum Kuta Bali",
        "type": "Отель",
        "description": "Комфортный отель в шаговой доступности от пляжа Куты.",
        "image": None,
    }),
    ("item", {
        "name": "The lava Bali Villa",
        "type": "Вилла",
        "description": "Уединённая вилла с собственным бассейном.",
        "image": None,
    }),
    ("item", {
        "name": "Hotel Shri Ganesh",
        "type": "Отель",
        "description": "Уютный отель в атмосферном районе острова.",
        "image": None,
    }),
    ("item", {
        "name": "Kura Kura Divers lodge",
        "type": "Лодж",
        "description": "Дайв-лодж для любителей подводного мира.",
        "image": None,
    }),
]

tour.cancel_policy = [
    ("item", {
        "period": "🔔 Предоплата",
        "description": "18 000 рублей — невозвратная, уходит на бронь отеля",
        "refund_percent": 0,
    }),
    ("item", {
        "period": "❗️ Остаток (180 000 р)",
        "description": "Оплачивается на месте в долларах или евро. Наличными. По курсу на день расчёта",
        "refund_percent": 0,
    }),
]

tour.save()
rev = tour.save_revision()
rev.publish()
print("OK: tour updated and published")
