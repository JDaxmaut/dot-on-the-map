<div align="center">

<br>

<img src="https://raw.githubusercontent.com/JDaxmaut/dot-on-the-map/main/static/img/hero-hills.webp" alt="Точка на карте" width="100%" style="border-radius:12px">

<br><br>

# Точка на карте

**Авторские туры по Азии — Бали · Япония · Вьетнам**

<br>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![Wagtail](https://img.shields.io/badge/Wagtail-7.4-43B1B0?style=flat-square&logo=wagtail&logoColor=white)](https://wagtail.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Alpine.js](https://img.shields.io/badge/Alpine.js-3.x-8BC0D0?style=flat-square&logo=alpine.js&logoColor=white)](https://alpinejs.dev)
[![License](https://img.shields.io/badge/License-MIT-C86B49?style=flat-square)](LICENSE)

</div>

---

## О проекте

**Точка на карте** — сайт туристического агентства, специализирующегося на авторских медленных турах по Азии. Небольшие группы, настоящие маршруты, уважение к местам и людям.

Сайт построен на Django + Wagtail CMS, что позволяет менеджерам редактировать туры, страницы и медиаконтент без написания кода — прямо через удобную admin-панель.

---

## Возможности

- **Каталог туров** — фильтрация по стране и тегу, карточки с ценой, датами и местами
- **Страницы туров** — слайдер фотографий, программа по дням, что включено/не включено, политика отмены
- **Форма заявки** — AJAX-отправка, матлогика CAPTCHA, чекбокс согласия на обработку ПД
- **Cookie-баннер** — соответствие 152-ФЗ и GDPR, сохраняется в browser cookie
- **Подписка на рассылку** — с валидацией согласия и CAPTCHA в футере
- **SEO** — автоматический `sitemap.xml` (Wagtail), `robots.txt`, meta-теги
- **Дизайн** — Tailwind CSS с фирменной палитрой, шрифты Cormorant Garamond + Inter
- **Производительность** — Lenis smooth scroll, WebP изображения, WhiteNoise, `will-change` оптимизация
- **Адаптивность** — корректное отображение от 320px до 4K
- **Юридическое** — страница реквизитов с ИНН/ОГРН/банковскими данными, правовые документы
- **CMS** — все страницы и туры редактируются через Wagtail admin без кода

---

## Стек технологий

| Слой | Технология |
|------|-----------|
| Backend | Django 6.0, Wagtail 7.4 |
| Frontend | Tailwind CSS 3, Alpine.js 3, Lenis 1.1 |
| База данных | SQLite (dev) / PostgreSQL (prod) |
| Статика | WhiteNoise, django-tailwind |
| Изображения | Pillow, Wagtail Images (авто WebP) |
| Деплой | python-decouple, WhiteNoise |

---

## Быстрый старт

### Требования

- Python 3.11+
- Node.js 18+ (для сборки Tailwind)

### Установка

```bash
# Клонировать репозиторий
git clone https://github.com/JDaxmaut/dot-on-the-map.git
cd dot-on-the-map

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env — задать SECRET_KEY, DEBUG и т.д.

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Установить Node.js зависимости и собрать CSS
python manage.py tailwind install
python manage.py tailwind build

# Наполнить базу тестовыми турами (опционально)
python manage.py populate_db

# Собрать статику
python manage.py collectstatic --noinput

# Запустить сервер
python manage.py runserver
```

Сайт доступен по адресу [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Admin-панель: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Переменные окружения

Файл `.env` (см. `.env.example`):

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

---

## Структура проекта

```
dot-on-the-map/
├── tochka/               # Конфигурация Django (settings, urls, wsgi)
├── tours/                # Основное приложение
│   ├── models.py         # Страницы Wagtail: HomePage, TourPage, ContactPage, AboutPage...
│   ├── forms.py          # ContactForm с валидацией
│   ├── blocks.py         # StreamField блоки
│   ├── migrations/       # Миграции БД
│   └── templates/
│       ├── base.html     # Базовый шаблон (nav, footer, cookie banner)
│       ├── 404.html      # Кастомная страница ошибки
│       ├── robots.txt    # SEO
│       └── tours/        # Шаблоны страниц
├── theme/                # django-tailwind приложение
│   └── static_src/       # Исходники Tailwind CSS
├── static/               # Статические файлы
│   ├── css/dist/         # Скомпилированный Tailwind
│   └── img/              # Изображения (hero-hills.webp и др.)
├── requirements.txt
├── .env.example
└── manage.py
```

---

## Wagtail CMS

Страницы управляются через Wagtail admin (`/admin/`):

| Модель | Описание |
|--------|----------|
| `HomePage` | Главная с hero, StreamField секциями |
| `CatalogPage` | Каталог туров с фильтрами |
| `TourPage` | Страница тура (цены, даты, программа, фото) |
| `ContactPage` | Контакты + форма заявки |
| `AboutPage` | О компании + реквизиты + банковские данные |
| `LegalPage` | Правовые документы (оферта, политика ПД) |

---

## Лицензия

MIT © 2026 [JDaxmaut](https://github.com/JDaxmaut)
