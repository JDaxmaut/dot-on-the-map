from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


# ── HOME PAGE BLOCKS ──────────────────────────────────────────

class ManifestBlock(blocks.StructBlock):
    numeral = blocks.CharBlock(default="01", label="Цифра")
    eyebrow = blocks.CharBlock(default="Философия пути", label="Надзаголовок")
    heading = blocks.CharBlock(label="Заголовок")
    body    = blocks.RichTextBlock(features=["bold", "italic"], label="Текст")
    stats   = blocks.ListBlock(
        blocks.StructBlock([
            ("value", blocks.CharBlock(label="Значение")),
            ("label", blocks.CharBlock(label="Подпись")),
        ]),
        label="Метрики",
    )

    class Meta:
        icon     = "pilcrow"
        label    = "Манифест"
        template = "blocks/manifest.html"


class DestinationCardBlock(blocks.StructBlock):
    title       = blocks.CharBlock(label="Направление")
    description = blocks.TextBlock(max_length=160, label="Описание (до 160 симв.)")
    price_from  = blocks.CharBlock(label="Цена от", help_text="Например: от $2 500")
    image       = ImageChooserBlock(label="Фото")
    link        = blocks.PageChooserBlock(required=False, label="Ссылка на страницу каталога")

    class Meta:
        icon     = "image"
        label    = "Карточка направления"
        template = "blocks/destination_card.html"


class QuoteBlock(blocks.StructBlock):
    quote  = blocks.TextBlock(label="Цитата")
    author = blocks.CharBlock(label="Автор / маршрут")

    class Meta:
        icon     = "openquote"
        label    = "Отзыв-цитата"
        template = "blocks/quote.html"


# ── TOUR PAGE BLOCKS ──────────────────────────────────────────

class DayBlock(blocks.StructBlock):
    day_number  = blocks.CharBlock(
        label="Номер дня / диапазон",
        help_text="Один день: «1», диапазон: «1-2». «День» добавляется автоматически.",
    )
    title       = blocks.CharBlock(label="Заголовок дня")
    description = blocks.RichTextBlock(
        features=["bold", "italic", "link"],
        label="Описание",
    )
    image = ImageChooserBlock(required=False, label="Фото дня")

    class Meta:
        icon     = "date"
        label    = "День маршрута"
        template = "blocks/day_block.html"


class AccommodationBlock(blocks.StructBlock):
    name        = blocks.CharBlock(label="Название отеля/виллы")
    type        = blocks.CharBlock(
        label="Тип и ночи",
        help_text="Например: Бутик-вилла · 3 ночи",
    )
    description = blocks.TextBlock(label="Описание")
    image       = ImageChooserBlock(required=False, label="Фото")

    class Meta:
        icon     = "home"
        label    = "Место проживания"
        template = "blocks/accommodation.html"


class CancelPolicyBlock(blocks.StructBlock):
    period         = blocks.CharBlock(label="Период", help_text="Например: За 30+ дней")
    description    = blocks.CharBlock(label="Описание")
    refund_percent = blocks.IntegerBlock(label="Возврат (%)", min_value=0, max_value=100)

    class Meta:
        icon  = "tick"
        label = "Условие возврата"


class FAQBlock(blocks.StructBlock):
    question = blocks.CharBlock(label="Вопрос")
    answer   = blocks.RichTextBlock(
        features=["bold", "italic", "link"],
        label="Ответ",
    )

    class Meta:
        icon  = "help"
        label = "Вопрос и ответ"


# ── ABOUT PAGE BLOCKS ─────────────────────────────────────────

class PartnerBlock(blocks.StructBlock):
    name            = blocks.CharBlock(label="Туроператор")
    registry_number = blocks.CharBlock(
        label="Реестровый номер ЕФР",
        required=False,
        help_text="Например: РТО-000001",
    )
    website         = blocks.URLBlock(label="Сайт", required=False)
    description     = blocks.TextBlock(
        label="Продукт / что реализуете",
        required=False,
    )

    class Meta:
        icon  = "group"
        label = "Туроператор-партнёр"


class CertificateBlock(blocks.StructBlock):
    title  = blocks.CharBlock(label="Название")
    issuer = blocks.CharBlock(label="Организация / реестр", required=False)
    number = blocks.CharBlock(label="Номер / дата", required=False)
    url    = blocks.URLBlock(label="Ссылка для проверки", required=False)

    class Meta:
        icon  = "tick-inverse"
        label = "Сертификат / членство"
