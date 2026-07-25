from django.core.management.base import BaseCommand
from wagtail.models import Page
from tours.models import EntryRulesIndexPage, EntryRuleCountryPage, HomePage


COUNTRY_DATA = [
    {
        "country_code": "vietnam",
        "title": "Вьетнам",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "45 дней (без визы), 90 дней (e-visa)",
        "notes": "<h2>Безвизовый въезд</h2><p>Для граждан РФ до 45 дней (продлено до 30.06.2025). Паспорт должен быть действителен минимум 6 месяцев от даты въезда.</p><h2>E-visa</h2><p>Выдаётся онлайн за 3–5 рабочих дней, срок действия 90 дней (однократный или многократный въезд).</p><p>Оформляется на <a href=\"https://evisa.xuatnhapcanh.gov.vn/\" target=\"_blank\" rel=\"noopener\">официальном портале</a>.</p><h2>Важно</h2><ul><li>Паспорт — 6+ месяцев</li><li>Билет туда-обратно</li></ul>",
    },
    {
        "country_code": "indonesia",
        "title": "Индонезия",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (VOA), до 60 дней (e-VOA с продлением)",
        "notes": "<h2>Visa on Arrival (VOA)</h2><p>$35 в аэропорту, продлевается ещё на 30 дней в иммиграции (итого 60 дней).</p><h2>e-VOA</h2><p>Оформляется заранее на <a href=\"https://molina.imigrasi.go.id/\" target=\"_blank\" rel=\"noopener\">molina.imigrasi.go.id</a> — $35.</p><p>Паспорт — не менее 6 месяцев, билет туда-обратно.</p>",
    },
    {
        "country_code": "china",
        "title": "Китай",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (без визы до 31.12.2025)",
        "notes": "<h2>Безвизовый въезд</h2><p>Для граждан РФ действует до 31 декабря 2025 года — до 30 дней для туризма, деловых поездок, посещения родственников и транзита.</p><h2>Обычная виза (L)</h2><p>Оформляется в визовом центре, срок до 90 дней, стоимость ~$30–140.</p><p>Требуется: паспорт 6+ месяцев, фото, бронь отеля, билет туда-обратно.</p>",
    },
    {
        "country_code": "cambodia",
        "title": "Камбоджа",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (продлевается на 30 дней)",
        "notes": "<h2>Visa on Arrival</h2><p>$30 в аэропортах Пномпена, Сием-Рипа, Сиануквиля и наземных переходах. Фото 4×6 см.</p><h2>E-visa</h2><p>$36 на <a href=\"https://www.evisa.gov.kh/\" target=\"_blank\" rel=\"noopener\">официальном сайте</a>, обработка 3 дня.</p><p>Паспорт — 6+ месяцев.</p>",
    },
    {
        "country_code": "japan",
        "title": "Япония",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": True,
        "max_stay": "90 дней (туристическая виза)",
        "notes": "<h2>E-visa</h2><p>Для граждан РФ доступна на <a href=\"https://www.evisa.go.jp/\" target=\"_blank\" rel=\"noopener\">japan.evisa.go.jp</a> (не требует поездки в консульство).</p><h2>Обычная виза</h2><p>Через визовый центр (VFS Global) — бесплатно для граждан РФ, сервисный сбор ~$30.</p><p>Нужны: паспорт, фото, справка с работы, выписка со счёта, бронь отеля и билеты, маршрут.</p>",
    },
    {
        "country_code": "laos",
        "title": "Лаос",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (продлевается до 60 дней)",
        "notes": "<h2>Visa on Arrival</h2><p>$30–42 в аэропортах Вьентьяна, Луангпрабанга, Паксе и наземных переходах. Фото 4×6 см.</p><h2>E-visa</h2><p>$30–45 на <a href=\"https://laoevisa.gov.la/\" target=\"_blank\" rel=\"noopener\">laoevisa.gov.la</a>, 3 дня обработка.</p><p>Паспорт — 6+ месяцев.</p>",
    },
    {
        "country_code": "malaysia",
        "title": "Малайзия",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (без визы)",
        "notes": "<h2>Безвизовый въезд</h2><p>Для граждан РФ до 30 дней. Паспорт — 6+ месяцев.</p><p><strong>MDAC:</strong> обязательно заполнить онлайн за 3 дня до въезда на <a href=\"https://imigresen-online.imi.gov.my/\" target=\"_blank\" rel=\"noopener\">imigresen-online.imi.gov.my</a> (бесплатно).</p><p>Билет туда-обратно могут запросить на границе.</p>",
    },
    {
        "country_code": "nepal",
        "title": "Непал",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "15/30/90 дней (на выбор)",
        "notes": "<h2>Visa on Arrival</h2><p>В аэропорту Катманду. Стоимость: 15 дней — $30, 30 дней — $50, 90 дней — $125.</p><h2>E-visa</h2><p>На <a href=\"https://nepal.immigration.gov.np/\" target=\"_blank\" rel=\"noopener\">nepal.immigration.gov.np</a>, те же цены.</p><p>Фото 2 шт. (есть автомат на месте). Паспорт — 6+ месяцев.</p>",
    },
    {
        "country_code": "philippines",
        "title": "Филиппины",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (без визы)",
        "notes": "<h2>Безвизовый въезд</h2><p>Для граждан РФ до 30 дней.</p><p><strong>eTravel:</strong> заполнить онлайн за 72 часа до вылета на <a href=\"https://etravel.gov.ph/\" target=\"_blank\" rel=\"noopener\">etravel.gov.ph</a>.</p><p>Паспорт — 6+ месяцев, билет вылета.</p>",
    },
    {
        "country_code": "thailand",
        "title": "Таиланд",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "60 дней (без визы)",
        "notes": "<h2>Безвизовый въезд</h2><p>Для граждан РФ до 60 дней. Продление на 30 дней в иммиграции за 1900 бат (~$55).</p><h2>E-visa</h2><p>Туристическая виза TR 60 дней на <a href=\"https://thaievisa.go.th/\" target=\"_blank\" rel=\"noopener\">thaievisa.go.th</a>.</p><p>Паспорт — 6+ месяцев, билет выезда.</p>",
    },
    {
        "country_code": "korea",
        "title": "Южная Корея",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": True,
        "max_stay": "90 дней (K-ETA / виза)",
        "notes": "<h2>K-ETA</h2><p>Электронное разрешение на <a href=\"https://www.k-eta.go.kr/\" target=\"_blank\" rel=\"noopener\">k-eta.go.kr</a> — $10, действует 2 года, до 90 дней.</p><h2>Туристическая виза (C-3-9)</h2><p>Через визовый центр, ~$40, до 90 дней.</p><p>Паспорт — 6+ месяцев, билет туда-обратно.</p>",
    },
]


class Command(BaseCommand):
    help = "Создание страниц стран для правил въезда"

    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if not home:
            self.stderr.write("HomePage не найдена")
            return

        index = EntryRulesIndexPage.objects.live().child_of(home).first()
        if not index:
            index = EntryRulesIndexPage(
                title="Правила въезда",
                slug="entry-rules",
                intro="<p>Актуальная информация о визах и правилах въезда для граждан РФ в популярные азиатские направления.</p>",
            )
            home.add_child(instance=index)
            index.save_revision().publish()
            self.stdout.write(f"Создана EntryRulesIndexPage (id={index.pk})")
        else:
            self.stdout.write(f"Найдена EntryRulesIndexPage (id={index.pk})")

        existing_codes = set(
            EntryRuleCountryPage.objects.live().child_of(index)
            .values_list("country_code", flat=True)
        )

        created = 0
        for c in COUNTRY_DATA:
            if c["country_code"] in existing_codes:
                self.stdout.write(f"  Пропущено: {c['title']} (уже существует)")
                continue

            page = EntryRuleCountryPage(
                title=c["title"],
                slug=c["country_code"],
                country_code=c["country_code"],
                visa_free=c["visa_free"],
                visa_on_arrival=c["visa_on_arrival"],
                e_visa=c["e_visa"],
                visa_required=c["visa_required"],
                max_stay=c["max_stay"],
                notes=c["notes"],
            )
            index.add_child(instance=page)
            page.save_revision().publish()
            created += 1
            self.stdout.write(f"  Создана: {page.title} -> /{page.slug}/")

        self.stdout.write(self.style.SUCCESS(f"Готово. Создано: {created}, всего: {len(COUNTRY_DATA)}"))