import random
from django.db import models
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from wagtail.models import Page, Orderable
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images import get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks as wt_blocks

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from .blocks import (
    DestinationCardBlock, ManifestBlock, QuoteBlock,
    DayBlock, AccommodationBlock, CancelPolicyBlock, FAQBlock,
    PartnerBlock, CertificateBlock,
)


# ─── TAGS ─────────────────────────────────────────────────────
class TourPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "TourPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


# ─── CONTACT SUBMISSION ───────────────────────────────────────
class ContactSubmission(models.Model):
    name       = models.CharField(_("Имя"), max_length=100)
    email      = models.EmailField(_("Email"))
    phone      = models.CharField(_("Телефон"), max_length=30, blank=True)
    tour       = models.CharField(_("Интересующий тур"), max_length=200, blank=True)
    message    = models.TextField(_("Сообщение"))
    created_at = models.DateTimeField(_("Дата"), auto_now_add=True)

    class Meta:
        verbose_name        = "Заявка"
        verbose_name_plural = "Заявки"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.email}"


# ─── HOME PAGE ────────────────────────────────────────────────
class HomePage(Page):
    hero_nav = True  # nav starts transparent (white text over dark hero)
    class Meta:
        verbose_name = "Главная страница"

    hero_eyebrow = models.CharField(_("Надзаголовок"), max_length=120,
                                    default="Авторские маршруты по Азии")
    hero_title   = models.CharField(_("Заголовок"), max_length=160,
                                    default="Замедлись, чтобы услышать Азию")
    hero_subtitle = models.TextField(_("Подзаголовок"), blank=True)
    hero_image   = models.ForeignKey(
        get_image_model_string(), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Главное фото"),
    )
    hero_cta_text = models.CharField(_("Текст CTA"), max_length=60,
                                     default="Смотреть направления")

    body = StreamField([
        ("manifest",     ManifestBlock()),
        ("destinations", DestinationCardBlock()),
        ("quote",        QuoteBlock()),
    ], use_json_field=True, blank=True, verbose_name=_("Секции"))

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_eyebrow"),
            FieldPanel("hero_title"),
            FieldPanel("hero_subtitle"),
            FieldPanel("hero_image"),
            FieldPanel("hero_cta_text"),
        ], heading="Hero"),
        FieldPanel("body"),
    ]

    subpage_types = ["tours.CatalogPage", "tours.ContactPage",
                     "tours.AboutPage", "tours.LegalPage"]


# ─── TOUR GALLERY IMAGE (inline child) ───────────────────────
class TourGalleryImage(Orderable):
    page    = ParentalKey("TourPage", on_delete=models.CASCADE,
                          related_name="gallery_images")
    image   = models.ForeignKey(
        get_image_model_string(), on_delete=models.CASCADE,
        related_name="+", verbose_name=_("Фото"),
    )
    caption = models.CharField(_("Подпись"), max_length=200, blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta(Orderable.Meta):
        verbose_name        = "Фото галереи"
        verbose_name_plural = "Фото галереи"


# ─── TOUR DATE (inline child) ─────────────────────────────────
class TourDate(models.Model):
    page        = ParentalKey("TourPage", on_delete=models.CASCADE,
                              related_name="tour_dates")
    start_date  = models.DateField(_("Дата заезда"))
    end_date    = models.DateField(_("Дата выезда"))
    price       = models.PositiveIntegerField(_("Цена (USD)"))
    total_spots = models.PositiveSmallIntegerField(_("Всего мест"), default=8)
    spots_left  = models.PositiveSmallIntegerField(_("Свободных мест"), default=8)

    @property
    def fill_percent(self):
        if self.total_spots == 0:
            return 100
        return round((self.total_spots - self.spots_left) / self.total_spots * 100)

    panels = [
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("price"),
        FieldPanel("total_spots"),
        FieldPanel("spots_left"),
    ]

    class Meta:
        ordering        = ["start_date"]
        verbose_name    = "Дата заезда"
        verbose_name_plural = "Даты заездов"


# ─── TOUR PAGE ────────────────────────────────────────────────
class TourPage(Page, ClusterableModel):
    hero_nav = True  # nav starts transparent over dark hero gallery
    class Meta:
        verbose_name = "Страница тура"

    location    = models.CharField(_("Локация"), max_length=120,
                                   help_text="Например: Индонезия · Бали")
    summary     = models.TextField(_("Краткое описание"))
    description = RichTextField(_("Подробное описание"), blank=True)
    highlights  = StreamField([("item", wt_blocks.CharBlock())],
                              use_json_field=True, blank=True,
                              verbose_name=_("Особенности тура"))

    duration        = models.CharField(_("Длительность"), max_length=40)
    group_size      = models.CharField(_("Размер группы"), max_length=40)
    group_size_max  = models.PositiveSmallIntegerField(_("Макс. мест"), default=8)
    comfort         = models.CharField(_("Проживание"), max_length=60, default="Бутик-виллы")
    difficulty      = models.CharField(_("Сложность"), max_length=40, default="Лёгкая")
    price_from      = models.CharField(_("Цена от"), max_length=40)
    country_tag     = models.CharField(_("Тег страны"), max_length=20,
                                       choices=[
                                           ("bali",    "Бали"),
                                           ("japan",   "Япония"),
                                           ("vietnam", "Вьетнам"),
                                       ],
                                       default="bali")

    @property
    def price_num(self):
        import re
        m = re.search(r'\d+', self.price_from.replace(',', '').replace(' ', ''))
        return int(m.group()) if m else 0

    tags = ClusterTaggableManager(through=TourPageTag, blank=True)

    hero_images = StreamField([("image", ImageChooserBlock())],
                              use_json_field=True, blank=True,
                              verbose_name=_("Галерея (3–5 фото)"))

    itinerary = StreamField([("day", DayBlock())],
                            use_json_field=True, blank=True,
                            verbose_name=_("Программа по дням"))

    accommodation = StreamField([("item", AccommodationBlock())],
                                use_json_field=True, blank=True,
                                verbose_name=_("Проживание"))

    included = StreamField([("item", wt_blocks.CharBlock())],
                           use_json_field=True, blank=True,
                           verbose_name=_("Включено"))
    excluded = StreamField([("item", wt_blocks.CharBlock())],
                           use_json_field=True, blank=True,
                           verbose_name=_("Не включено"))

    cancel_policy = StreamField([("item", CancelPolicyBlock())],
                                use_json_field=True, blank=True,
                                verbose_name=_("Политика отмены"))
    force_majeure_note = models.TextField(
        _("Сноска о форс-мажоре"), blank=True,
        default="При форс-мажоре (стихийные бедствия, закрытие границ) возврат — 100% независимо от срока.",
    )

    what_to_bring = StreamField(
        [("item", wt_blocks.CharBlock(label="Пункт"))],
        use_json_field=True, blank=True,
        verbose_name=_("Что взять с собой"),
    )

    faq = StreamField(
        [("item", FAQBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Частые вопросы (FAQ)"),
    )

    cta_heading = models.CharField(
        _("Заголовок финального CTA"), max_length=160,
        default="Готовы почувствовать настоящую Азию?",
    )
    cta_button = models.CharField(
        _("Текст кнопки CTA"), max_length=60,
        default="Выбрать дату",
    )

    content_panels = Page.content_panels + [

        MultiFieldPanel([
            FieldPanel("hero_images"),
        ], heading="Главная галерея (hero, 3–5 фото)"),

        MultiFieldPanel([
            FieldPanel("location"),
            FieldPanel("country_tag"),
            FieldPanel("summary"),
            FieldPanel("description"),
            FieldPanel("highlights"),
            FieldPanel("tags"),
        ], heading="Описание тура"),

        MultiFieldPanel([
            FieldPanel("duration"),
            FieldPanel("group_size"),
            FieldPanel("group_size_max"),
            FieldPanel("comfort"),
            FieldPanel("difficulty"),
            FieldPanel("price_from"),
        ], heading="Параметры тура"),

        InlinePanel("tour_dates", label="Даты и цены заездов"),

        FieldPanel("itinerary"),

        InlinePanel("gallery_images", label="Галерея тура (до 10 фото)", max_num=10),

        FieldPanel("accommodation"),

        FieldPanel("what_to_bring"),

        MultiFieldPanel([
            FieldPanel("included"),
            FieldPanel("excluded"),
        ], heading="Включено / не включено"),

        FieldPanel("faq"),

        MultiFieldPanel([
            FieldPanel("cancel_policy"),
            FieldPanel("force_majeure_note"),
        ], heading="Политика отмены"),

        MultiFieldPanel([
            FieldPanel("cta_heading"),
            FieldPanel("cta_button"),
        ], heading="Финальный призыв к действию"),
    ]

    parent_page_types = ["tours.CatalogPage"]


# ─── CATALOG PAGE ─────────────────────────────────────────────
class CatalogPage(Page):
    class Meta:
        verbose_name = "Каталог туров"

    intro = models.TextField(_("Подзаголовок"), blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types   = ["tours.TourPage"]
    parent_page_types = ["tours.HomePage"]

    def get_context(self, request):
        context = super().get_context(request)
        tours = TourPage.objects.live().child_of(self).order_by("title")

        tag = request.GET.get("filter", "all")
        if tag != "all":
            tours = tours.filter(country_tag=tag)

        q = request.GET.get("q", "").strip()
        if q:
            tours = tours.filter(title__icontains=q)

        sort = request.GET.get("sort", "default")
        if sort == "price_asc":
            tours = sorted(tours, key=lambda t: int(t.price_from.replace("$", "").replace(" ", "").replace(",", "") or 0))
        elif sort == "price_desc":
            tours = sorted(tours, key=lambda t: int(t.price_from.replace("$", "").replace(" ", "").replace(",", "") or 0), reverse=True)

        context["tours"] = tours

        # Генерируем фильтры из реальных данных БД — автоматически обновляются
        choices_map = {c[0]: c[1] for c in TourPage._meta.get_field("country_tag").choices}
        live_tags = (
            TourPage.objects.live().child_of(self)
            .exclude(country_tag="")
            .values_list("country_tag", flat=True)
            .distinct()
            .order_by("country_tag")
        )
        context["filter_tags"] = [{"id": "all", "label": "Все"}] + [
            {"id": tag, "label": choices_map.get(tag, tag.capitalize())}
            for tag in live_tags
        ]
        context["sort_options"] = [
            {"id": "default",    "label": "Подборка"},
            {"id": "price_asc",  "label": "Дешевле"},
            {"id": "price_desc", "label": "Дороже"},
        ]
        return context


# ─── CONTACT PAGE ─────────────────────────────────────────────
class ContactPage(Page):
    class Meta:
        verbose_name = "Страница контактов"

    intro     = RichTextField(_("Вступление"), blank=True)
    email     = models.EmailField(_("Email"), default="hello@tochka.travel")
    telegram  = models.URLField(_("Telegram"), blank=True)
    whatsapp  = models.URLField(_("WhatsApp"), blank=True)
    address   = models.CharField(_("Адрес"), max_length=200, blank=True)
    hours     = models.CharField(_("Часы работы"), max_length=120, blank=True)
    side_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Фото сбоку"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel([
            FieldPanel("email"),
            FieldPanel("telegram"),
            FieldPanel("whatsapp"),
            FieldPanel("address"),
            FieldPanel("hours"),
        ], heading="Контакты"),
        FieldPanel("side_image"),
    ]

    parent_page_types = ["tours.HomePage"]

    def serve(self, request):
        if (request.method == "POST"
                and request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"):
            from .forms import ContactForm
            form = ContactForm(request.POST)
            errors = {}

            # Validate math captcha
            try:
                user_ans = int(request.POST.get("captcha_answer", ""))
                captcha_ok = user_ans == request.session.get("captcha_answer")
            except (ValueError, TypeError):
                captcha_ok = False
            if not captcha_ok:
                errors["captcha_answer"] = ["Неверный ответ. Попробуйте ещё раз."]

            # Validate consent
            if not request.POST.get("consent"):
                errors["consent"] = ["Необходимо дать согласие на обработку данных."]

            if form.is_valid() and not errors:
                form.save()
                return JsonResponse({"success": True})

            errors.update({k: list(v) for k, v in form.errors.items()})
            return JsonResponse({"success": False, "errors": errors}, status=400)

        return super().serve(request)

    def get_context(self, request):
        from .forms import ContactForm
        context = super().get_context(request)

        initial = {}
        tour_name = request.GET.get("tour", "").strip()
        date_info = request.GET.get("date", "").strip()
        if tour_name:
            initial["tour"] = f"{tour_name} · {date_info}" if date_info else tour_name
        context["form"] = ContactForm(initial=initial)

        # Generate math captcha and store answer in session
        a, b = random.randint(1, 9), random.randint(1, 9)
        request.session["captcha_answer"] = a + b
        request.session.modified = True
        context["captcha_a"] = a
        context["captcha_b"] = b
        return context


# ─── LEGAL PAGE ───────────────────────────────────────────────
class LegalPage(Page):
    class Meta:
        verbose_name        = "Правовой документ"
        verbose_name_plural = "Правовые документы"

    intro   = models.TextField(_("Краткое описание"), blank=True,
                               help_text="Одна строка под заголовком")
    content = RichTextField(
        _("Содержание"),
        features=["h2", "h3", "h4", "bold", "italic", "ol", "ul", "link", "hr"],
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("content"),
    ]

    parent_page_types = ["tours.HomePage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["sibling_docs"] = (
            LegalPage.objects.live()
            .sibling_of(self, inclusive=False)
            .order_by("title")
        )
        return context


# ─── ABOUT PAGE ───────────────────────────────────────────────
class AboutPage(Page):
    class Meta:
        verbose_name = "О компании"

    # Hero / intro
    intro      = models.TextField(_("Вступление"), blank=True)
    hero_image = models.ForeignKey(
        get_image_model_string(), null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Фото для hero"),
    )
    about_text = RichTextField(
        _("О нас (подробно)"), blank=True,
        features=["h2", "h3", "bold", "italic", "ol", "ul", "link"],
    )

    # Legal identifiers
    company_full_name = models.CharField(_("Полное юридическое наименование"),
                                         max_length=400, blank=True)
    legal_address     = models.TextField(_("Юридический адрес"), blank=True)
    actual_address    = models.TextField(_("Фактический адрес"), blank=True)
    ogrn              = models.CharField(_("ОГРН / ОГРНИП"), max_length=20, blank=True)
    inn               = models.CharField(_("ИНН"), max_length=15, blank=True)
    kpp               = models.CharField(_("КПП"), max_length=9, blank=True)

    # Bank details
    bank_name         = models.CharField(_("Банк"), max_length=300, blank=True)
    bank_bik          = models.CharField(_("БИК"), max_length=9, blank=True)
    bank_city         = models.CharField(_("Город банка"), max_length=100, blank=True)
    bank_settlement   = models.CharField(_("Расчётный счёт"), max_length=20, blank=True)
    bank_corr         = models.CharField(_("Корр. счёт"), max_length=20, blank=True)

    # Tour operator info
    is_operator         = models.BooleanField(_("Является туроператором"), default=False)
    registry_number     = models.CharField(
        _("Реестровый номер ЕФР туроператоров"),
        max_length=50, blank=True,
        help_text="Например: РТО-000001",
    )
    financial_guarantee = models.TextField(
        _("Финансовое обеспечение"), blank=True,
        help_text="Размер и наименование организации-гаранта",
    )

    # Partners / principals
    partners = StreamField(
        [("partner", PartnerBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Туроператоры-партнёры (принципалы)"),
    )

    # Certificates / memberships
    certificates = StreamField(
        [("cert", CertificateBlock())],
        use_json_field=True, blank=True,
        verbose_name=_("Сертификаты и членство в ассоциациях"),
    )

    # Contacts (displayed on this page)
    email    = models.EmailField(_("Email"), blank=True)
    phone    = models.CharField(_("Телефон"), max_length=30, blank=True)
    telegram = models.URLField(_("Telegram"), blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("intro"),
            FieldPanel("hero_image"),
            FieldPanel("about_text"),
        ], heading="О компании"),

        MultiFieldPanel([
            FieldPanel("company_full_name"),
            FieldPanel("ogrn"),
            FieldPanel("inn"),
            FieldPanel("kpp"),
            FieldPanel("legal_address"),
            FieldPanel("actual_address"),
        ], heading="Юридическая информация"),

        MultiFieldPanel([
            FieldPanel("bank_name"),
            FieldPanel("bank_bik"),
            FieldPanel("bank_city"),
            FieldPanel("bank_settlement"),
            FieldPanel("bank_corr"),
        ], heading="Банковские реквизиты"),

        MultiFieldPanel([
            FieldPanel("is_operator"),
            FieldPanel("registry_number"),
            FieldPanel("financial_guarantee"),
        ], heading="Туроператор"),

        FieldPanel("partners"),
        FieldPanel("certificates"),

        MultiFieldPanel([
            FieldPanel("email"),
            FieldPanel("phone"),
            FieldPanel("telegram"),
        ], heading="Контакты"),
    ]

    parent_page_types = ["tours.HomePage"]
