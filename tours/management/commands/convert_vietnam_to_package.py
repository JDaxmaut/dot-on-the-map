"""
python manage.py convert_vietnam_to_package

Конвертирует страницу «Вьетнам с надёжным принимающим туроператором»
(ТурPage -> PackageTourPage) без смены URL.

Фото отелей и hero-галерея переиспользуются. Старое содержание (даты,
программа по дням, галерея, FAQ) удаляется вместе со страницей.
"""
import json

from django.core.management.base import BaseCommand


SLUG = "vietnam-s-nadezhnym-prinimayushchim-turoperatorom"

DESCRIPTION = (
    "<p>Мы — официальный партнер одного из ведущих принимающих туроператоров "
    "Вьетнама. Благодаря прямому сотрудничеству мы предлагаем выгодные пакетные "
    "туры с прямыми рейсами из Москвы и других городов России (уточняйте) на "
    "лучшие курорты страны.</p>"
    "<h3>В нашей подборке:</h3>"
    "<ul>"
    "<li>Нячанг</li>"
    "<li>Дананг</li>"
    "<li>Фукуок</li>"
    "<li>лучшие отели Вьетнама</li>"
    "<li>туры от 7 ночей</li>"
    "<li>цены от 67 000 ₽ за человека</li>"
    "</ul>"
    "<h3>В стоимость тура уже входят:</h3>"
    "<ul>"
    "<li>прямой перелет из Москвы, Владивостока, Благовещенска, Хабаровска, "
    "Новокузнецка, Барнаула, Новосибирска, Казани, Красноярска</li>"
    "<li>проживание в выбранном отеле</li>"
    "<li>поддержка надежного принимающего туроператора во Вьетнаме</li>"
    "</ul>"
    "<p>Мы работаем напрямую с принимающей стороной, поэтому предлагаем "
    "актуальные спецпредложения, широкий выбор проверенных отелей и лучшие "
    "условия для отдыха.</p>"
    "<p>Оставьте заявку, и мы бесплатно подберем для вас оптимальный вариант "
    "отдыха с учетом ваших пожеланий и бюджета. Предложений очень много — "
    "поможем выбрать именно тот тур, который подойдет вам лучше всего!</p>"
)


def resort_of(hotel_type):
    return (hotel_type or "Отели").split(" ·")[0].strip()


class Command(BaseCommand):
    help = "Конвертирует тур по Вьетнаму в пакетный (PackageTourPage), сохраняя URL."

    def handle(self, *args, **options):
        from wagtail.images import get_image_model
        from tours.models import CatalogPage, PackageTourPage, TourPage

        old = TourPage.objects.filter(slug=SLUG).first()
        if not old:
            self.stderr.write(f"Тур не найден: {SLUG}")
            return

        catalog = old.get_parent()

        # Достаём данные до удаления страницы
        hero_ids = [b.value for b in old.hero_images if b.value]
        hotels = []
        for b in old.accommodation:
            v = b.value
            if not v or not v.get("name"):
                continue
            hotels.append({
                "name": v.get("name"),
                "type": v.get("type", ""),
                "description": v.get("description", ""),
                "image": v.get("image"),
            })

        Image = get_image_model()

        def img(value):
            if value is None:
                return None
            if isinstance(value, Image):
                return value
            try:
                return Image.objects.get(pk=int(value))
            except (TypeError, ValueError, Image.DoesNotExist):
                return None

        # Группируем отели по курорту, сохраняя порядок первого вхождения
        sections = []
        order = {}
        for h in hotels:
            resort = resort_of(h.get("type"))
            if resort not in order:
                order[resort] = len(sections)
                sections.append({"resort": resort, "hotels": []})
            sections[order[resort]]["hotels"].append({
                "name": h["name"],
                "type": h["type"],
                "description": h["description"],
                "image": img(h["image"]),
            })

        hero_images = [("image", i) for i in (img(i) for i in hero_ids) if i]

        self.stdout.write(
            f"Старая страница: «{old.title}» (id={old.pk}). "
            f"Отелей: {len(hotels)}, курортов: {len(sections)}."
        )

        # Удаляем старую страницу и создаём пакетную с тем же slug
        old.delete()

        package = PackageTourPage(
            title="Вьетнам с надёжным принимающим туроператором",
            slug=SLUG,
            location="Вьетнам · Дананг · Нячанг · Фукуок",
            summary=(
                "Пакетные туры во Вьетнам от надёжного принимающего туроператора: "
                "прямые рейсы, лучшие отели Дананга, Нячанга и Фукуока — от 67 000 ₽."
            ),
            description=DESCRIPTION,
            duration="от 7 ночей",
            price_from="от 67 000 ₽",
            country_tag="vietnam",
            hero_images=hero_images,
            hotel_sections=[
                ("section", {
                    "resort": s["resort"],
                    "hotels": [
                        {"name": h["name"], "type": h["type"],
                         "description": h["description"], "image": h["image"]}
                        for h in s["hotels"]
                    ],
                })
                for s in sections
            ],
            cta_heading="Подберём тур, который подойдёт именно вам",
            cta_button="Подобрать тур",
            seo_title=(
                "Пакетные туры во Вьетнам: Дананг, Нячанг, Фукуок от 67 000 ₽ "
                "| Точка на карте"
            ),
            search_description=(
                "Пакетные туры во Вьетнам с прямыми рейсами и надёжным принимающим "
                "туроператором: лучшие отели Дананга, Нячанга и Фукуока от 67 000 ₽."
            ),
        )

        catalog.add_child(instance=package)
        package.save_revision().publish()

        self.stdout.write(self.style.SUCCESS(
            f"OK Пакетный тур создан: /catalog/{SLUG}/ (id={package.pk})"
        ))
        self.stdout.write(
            f"  Секции отелей: {[(s['resort'], len(s['hotels'])) for s in sections]}"
        )
        self.stdout.write(
            f"  Hero фото: {[b.value for b in package.hero_images]}"
        )
