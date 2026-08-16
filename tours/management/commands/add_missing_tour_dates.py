"""
python manage.py add_missing_tour_dates

Добавляет конкретные даты заездов турам, у которых они были только в тексте
dates_info (по данным исходных документов в «туры/инздонеия и тд»):

- shankhay-bali-ubud / shankhay-bali-novyy-god: вылеты 27.12.26, 29.12.26, 04.01.27
  (29.12 — 13 дней/12 ночей; 27.12 и 04.01 — 14 дней/13 ночей).
- pekin-shankhay: 13 заездов по 7 дней/6 ночей в Китае;
  с перелётом (вылет на 1 день раньше) и без перелёта.

Идемпотентна: при наличии дат пропускает.
"""
import datetime

from django.core.management.base import BaseCommand


def add(pk, dates_info_new, rows):
    from tours.models import TourDate, TourPage
    tour = TourPage.objects.get(pk=pk)
    created = 0
    if dates_info_new is not None and tour.dates_info != dates_info_new:
        tour.dates_info = dates_info_new
        tour.save_revision().publish()
    if not TourDate.objects.filter(page=tour).exists():
        for start, end, price, currency in rows:
            TourDate.objects.create(
                page=tour, start_date=start, end_date=end,
                price=price, currency=currency,
                total_spots=6, spots_left=6,
            )
            created += 1
    return tour, created


class Command(BaseCommand):
    help = "Добавляет конкретные даты заездов турам без TourDate."

    def handle(self, *args, **options):
        d = datetime.date

        # Шанхай — Бали — Убуд (13/14 дней, от $2 463)
        tour, n = add(
            51, "27.12.26, 29.12.26, 04.01.27",
            [
                (d(2026, 12, 27), d(2027, 1, 9), 2463, "USD"),
                (d(2026, 12, 29), d(2027, 1, 10), 2463, "USD"),
                (d(2027, 1, 4), d(2027, 1, 17), 2463, "USD"),
            ],
        )
        self.stdout.write(f"{tour.slug}: создано {n} дат")

        # Шанхай — Бали (13/14 дней, от $2 358)
        tour, n = add(
            58, "27.12.26, 29.12.26, 04.01.27",
            [
                (d(2026, 12, 27), d(2027, 1, 9), 2358, "USD"),
                (d(2026, 12, 29), d(2027, 1, 10), 2358, "USD"),
                (d(2027, 1, 4), d(2027, 1, 17), 2358, "USD"),
            ],
        )
        self.stdout.write(f"{tour.slug}: создано {n} дат")

        # Пекин + Шанхай (8 дней с перелётом / 7 дней без, заезды 7 дней/6 ночей)
        starts = [
            (2026, 8, 24), (2026, 9, 5), (2026, 9, 19),
            (2026, 10, 12), (2026, 10, 26), (2026, 11, 2),
            (2026, 11, 23), (2027, 2, 22), (2027, 3, 8),
            (2027, 4, 5), (2027, 4, 19), (2027, 5, 3), (2027, 5, 24),
        ]
        rows = []
        for y, m, day in starts:
            z = d(y, m, day)
            end = z + datetime.timedelta(days=6)   # 7 дней / 6 ночей в Китае
            rows.append((z - datetime.timedelta(days=1), end, 1385, "USD"))  # с перелётом, вылет на 1 день раньше
            rows.append((z, end, 864, "USD"))                                 # без перелёта
        tour, n = add(53, None, rows)
        self.stdout.write(f"{tour.slug}: создано {n} дат")

        self.stdout.write(self.style.SUCCESS("Готово."))
