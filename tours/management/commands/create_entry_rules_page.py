import json
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from tours.models import EntryRulesPage, HomePage


COUNTRY_DATA = [
    {
        "country": "vietnam",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "45 дней (без визы), 90 дней (e-visa)",
        "notes": "<p><strong>Без визы:</strong> для граждан РФ до 45 дней (до 30.06.2025 продлено до 45 дней).</p><p><strong>E-visa:</strong> выдаётся онлайн за 3–5 рабочих дней, срок действия 90 дней (одиночное или множественное въезд). Оформляется на <a href=\"https://evisa.xuatnhapcanh.gov.vn/\" target=\"_blank\" rel=\"noopener\">официальном портале</a>.</p><p>Паспорт должен быть действителен минимум 6 месяцев от даты въезда.</p>",
    },
    {
        "country": "indonesia",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (VOA), до 60 дней (e-VOA)",
        "notes": "<p><strong>Visa on Arrival (VOA):</strong> $35 (IDR 500 000) в аэропорту, продлевается ещё на 30 дней в иммиграции (итого 60 дней). Оплата картой или наличными.</p><p><strong>e-VOA:</strong> оформляется онлайн заранее на <a href=\"https://molina.imigrasi.go.id/\" target=\"_blank\" rel=\"noopener\">molina.imigrasi.go.id</a>, то же $35, ускоряет прохождение границы.</p><p><strong>Важно:</strong> паспорт — не менее 6 месяцев, билет туда-обратно, доказательство средств (~$2000 или бронь отеля).</p>",
    },
    {
        "country": "china",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (без визы до 31.12.2025)",
        "notes": "<p><strong>Безвизовый въезд для граждан РФ:</strong> действует до 31 декабря 2025 года включительно — до 30 дней для туризма, деловых поездок, посещения родственников и транзита.</p><p><strong>Обычная виза (L):</strong> если безвиз не подходит — оформляется в визовом центре (Москва, СПб, Екатеринбург и др.), срок до 90 дней, стоимость ~$30–140 в зависимости от типа и срочности.</p><p>Требуется: паспорт 6+ месяцев, фото, бронь отеля/приглашение, билет туда-обратно.</p>",
    },
    {
        "country": "cambodia",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (продлевается на 30 дней)",
        "notes": "<p><strong>Visa on Arrival:</strong> $30 (туристическая T-class) в аэропортах Пномпена, Сием-Рипа, Сиаунуквилля и на наземных переходах. Фото 4×6 см (можно сделать на месте).</p><p><strong>E-visa:</strong> $36 на <a href=\"https://www.evisa.gov.kh/\" target=\"_blank\" rel=\"noopener\">официальном сайте</a>, обработка 3 дня, въезд только через основные аэропорты и некоторые наземные пункты.</p><p>Продление — ещё 30 дней в иммиграции Пномпена/Сием-Рипа ($45–50). Паспорт — 6+ месяцев.</p>",
    },
    {
        "country": "japan",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": True,
        "max_stay": "90 дней (туристская виза)",
        "notes": "<p><strong>E-visa для туристов:</strong> с 2023 года доступна для граждан РФ (одиночная, до 90 дней). Оформляется на <a href=\"https://www.evisa.go.jp/\" target=\"_blank\" rel=\"noopener\">japan.evisa.go.jp</a> — не требуется поездка в консульство.</p><p><strong>Обычная виза:</strong> через визовый центр (VFS Global), срок рассмотрения 4+ дней, стоимость ~$0 (бесплатно для граждан РФ с 2019 г., сервисный сбор центра ~$30).</p><p>Нужны: паспорт, фото, справка с работы/учебы, выписка со счёта, бронь отеля и билеты, маршрут по дням.</p>",
    },
    {
        "country": "laos",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "30 дней (продлевается до 60 дней)",
        "notes": "<p><strong>Visa on Arrival:</strong> $30–42 (зависит от национальности) в аэропортах Вьентьяна, Луанг-Прабанга, Паксэ и на наземных переходах. Фото 4×6 см.</p><p><strong>E-visa:</strong> на <a href=\"https://laoevisa.gov.la/\" target=\"_blank\" rel=\"noopener\">официальном сайте</a>, обработка 3 дня, въезд через основные пункты.</p><p>Продление — в иммиграции Вьентьяна/Луанг-Прабанга. Паспорт — 6+ месяцев.</p>",
    },
    {
        "country": "malaysia",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (без визы)",
        "notes": "<p><strong>Безвизовый въезд для граждан РФ:</strong> до 30 дней для туризма. Паспорт — минимум 6 месяцев от даты въезда.</p><p>Миграционная карта заполняется онлайн заранее на <a href=\"https://imigresen-online.imi.gov.my/\" target=\"_blank\" rel=\"noopener\">портле MDAC</a> (Malaysia Digital Arrival Card) — не позднее 3 дней до прилёта.</p><p>Билет туда-обратно и доказательство средств могут запросить на границе.</p>",
    },
    {
        "country": "nepal",
        "visa_free": False,
        "visa_on_arrival": True,
        "e_visa": True,
        "visa_required": False,
        "max_stay": "15/30/90 дней (по выбору)",
        "notes": "<p><strong>Visa on Arrival:</strong> в аэропорту Катманду и на наземных переходах. Стоимость: 15 дней — $30, 30 дней — $50, 90 дней — $125. Оплата наличными (USD) или картой.</p><p><strong>E-visa:</strong> на <a href=\"https://nepaliport.immigration.gov.np/\" target=\"_blank\" rel=\"noopener\">непальском портале</a>, упрощает въезд.</p><p>Фото 2 шт. (можно сделать на месте). Паспорт — 6+ месяцев. Продление — в иммиграции Катманду.</p>",
    },
    {
        "country": "philippines",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "30 дней (без визы)",
        "notes": "<p><strong>Безвизовый въезд для граждан РФ:</strong> до 30 дней для туризма. Паспорт — 6+ месяцев от даты въезда.</p><p>Обязательно: билет туда-обратно (или на продолжительном рейсе), доказательство средств проживания.</p><p>Миграционная карта eTravel — онлайн за 72 часа до прилёта: <a href=\"https://etravel.gov.ph/\" target=\"_blank\" rel=\"noopener\">etravel.gov.ph</a>.</p><p>Продление — в иммиграции (Bureau of Immigration) до 36 месяцев суммарно.</p>",
    },
    {
        "country": "thailand",
        "visa_free": True,
        "visa_on_arrival": False,
        "e_visa": False,
        "visa_required": False,
        "max_stay": "60 дней (без визы до 2025), 30 дней (стандарт)",
        "notes": "<p><strong>Без визы для граждан РФ:</strong> продлён до 60 дней (акция до 31.12.2025). Стандартный безвиз — 30 дней.</p><p>Миграционная карта TM6 — онлайн на <a href=\"https://tdac.immigration.go.th/\" target=\"_blank\" rel=\"noopener\">TDAC</a> (Thailand Digital Arrival Card) заранее.</p><p><strong>Виза TR (60 дней):</strong> оформляется в консульстве/визовом центре, продлевается на 30 дней в иммиграции (итого 90 дней).</p><p>Паспорт — 6+ месяцев. Билет туда-обратно обязателен.</p>",
    },
    {
        "country": "korea",
        "visa_free": False,
        "visa_on_arrival": False,
        "e_visa": True,
        "visa_required": True,
        "max_stay": "90 дней (K-ETA / туристическая виза)",
        "notes": "<p><strong>K-ETA (электронное разрешение):</strong> обязательно для безвизового въезда (до 90 дней). Оформляется на <a href=\"https://www.k-eta.go.kr/\" target=\"_blank\" rel=\"noopener\">k-eta.go.kr</a> или приложении, $10, действует 2 года.</p><p><strong>Обычная виза (C-3-9):</strong> если K-ETA не подходит — через визовый центр, 90 дней, стоимость ~$40+.</p><p>С 2024 года K-ETA обязателен для граждан РФ для поездок до 90 дней. Паспорт — 6+ месяцев, билет туда-обратно.</p>",
    },
]


class Command(BaseCommand):
    help = "Create EntryRulesPage with 11 countries data"

    def handle(self, *args, **options):
        # Find home page
        home = HomePage.objects.first()
        if not home:
            self.stderr.write("HomePage not found")
            return

        # Check if already exists
        existing = EntryRulesPage.objects.live().child_of(home).first()
        if existing:
            self.stdout.write(f"EntryRulesPage already exists: {existing.title} (id={existing.pk})")
            page = existing
        else:
            page = EntryRulesPage(
                title="Правила въезда",
                slug="entry-rules",
                intro="<p>Актуальная информация о визах и правилах въезда для граждан РФ в популярные азиатские направления. Правила могут меняться — проверяйте официальные источники перед поездкой.</p>",
            )
            home.add_child(instance=page)
            self.stdout.write(f"Created EntryRulesPage: {page.title} (id={page.pk})")

        # Build StreamField data
        stream_data = []
        for c in COUNTRY_DATA:
            stream_data.append({
                "type": "country",
                "value": c,
            })

        page.countries = stream_data
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"Updated {len(stream_data)} countries on page"))

        # Show URL
        self.stdout.write(f"URL: {page.full_url}")