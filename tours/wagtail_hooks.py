from datetime import date

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component


# ── Кастомная тема ────────────────────────────────────────────
@hooks.register("insert_global_admin_css")
def admin_custom_css():
    return format_html('<link rel="stylesheet" href="{}?v=3">', static("tours/admin_theme.css"))


# ── Панель: быстрые действия ───────────────────────────────────
class QuickActionsPanel(Component):
    name = "quick_actions"
    order = 49

    def render_html(self, parent_context=None):
        from tours.models import CatalogPage
        catalog = CatalogPage.objects.first()
        html = render_to_string("wagtailadmin/panels/quick_actions.html", {
            "catalog_id": catalog.pk if catalog else None,
        })
        return mark_safe(html)


# ── Панель: черновики туров ────────────────────────────────────
class DraftToursPanel(Component):
    name = "draft_tours"
    order = 50

    def render_html(self, parent_context=None):
        from tours.models import TourPage
        drafts = TourPage.objects.filter(live=False).order_by("title")
        if not drafts.exists():
            return mark_safe("")
        html = render_to_string("wagtailadmin/panels/draft_tours.html", {
            "drafts": drafts,
        })
        return mark_safe(html)


# ── Панель: ближайшие заезды ───────────────────────────────────
class UpcomingDatesPanel(Component):
    name = "upcoming_dates"
    order = 51

    def render_html(self, parent_context=None):
        from tours.models import TourDate
        dates = (
            TourDate.objects
            .filter(start_date__gte=date.today())
            .select_related("page")
            .order_by("start_date")[:20]
        )
        html = render_to_string("wagtailadmin/panels/upcoming_dates.html", {
            "dates": dates,
        })
        return mark_safe(html)


# ── Дашборд: собираем панели ───────────────────────────────────
@hooks.register("construct_homepage_panels")
def customize_homepage_panels(request, panels):
    keep = {"site_summary"}
    panels[:] = [p for p in panels if getattr(p, "name", None) in keep]
    panels.insert(0, QuickActionsPanel())
    panels.insert(1, DraftToursPanel())
    panels.append(UpcomingDatesPanel())


# ── Страница «Мои туры» ────────────────────────────────────────
def tours_admin_view(request):
    from tours.models import TourPage, CatalogPage
    catalog = CatalogPage.objects.first()
    all_tours = TourPage.objects.all().order_by("title")
    return render(request, "wagtailadmin/tours_list.html", {
        "live_tours":  [t for t in all_tours if t.live],
        "draft_tours": [t for t in all_tours if not t.live],
        "catalog_id":  catalog.pk if catalog else None,
    })


# ── URL-ы ──────────────────────────────────────────────────────
@require_POST
def quick_save_dates(request):
    from tours.models import TourDate
    dates = TourDate.objects.filter(start_date__gte=date.today())
    for d in dates:
        changed = False
        if f"price_{d.pk}" in request.POST:
            try:
                d.price = int(request.POST[f"price_{d.pk}"])
                changed = True
            except ValueError:
                pass
        if f"spots_{d.pk}" in request.POST:
            try:
                d.spots_left = max(0, min(int(request.POST[f"spots_{d.pk}"]), d.total_spots))
                changed = True
            except ValueError:
                pass
        if changed:
            d.save()
    return HttpResponseRedirect("/admin/")


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("tour-dates/quick-save/", quick_save_dates, name="quick_save_dates"),
        path("moi-tury/", tours_admin_view, name="tours_admin_list"),
    ]


# ── Пункт меню «Туры» ─────────────────────────────────────────
@hooks.register("register_admin_menu_item")
def register_tours_menu_item():
    return MenuItem("Туры", "/admin/moi-tury/", icon_name="list-ul", order=200)


# ── Кнопка «Открыть» в списке страниц ─────────────────────────
@hooks.register("construct_page_listing_buttons")
def add_open_button(buttons, page, user, context=None):
    from tours.models import TourPage
    from wagtail.admin.widgets import PageListingButton
    if isinstance(page, TourPage) and page.live:
        buttons.append(PageListingButton(
            "Открыть",
            page.full_url,
            attrs={"target": "_blank", "rel": "noopener"},
            priority=20,
        ))


# ── Убираем лишние пункты главного меню ───────────────────────
@hooks.register("construct_main_menu")
def hide_menu_items(request, menu_items):
    remove = {"help", "reports"}
    menu_items[:] = [i for i in menu_items if i.name not in remove]


# ── Убираем лишние пункты меню «Настройки» ────────────────────
@hooks.register("construct_settings_menu")
def hide_settings_items(request, menu_items):
    remove = {"workflows", "workflow-tasks"}
    menu_items[:] = [i for i in menu_items if i.name not in remove]
