from wagtail import hooks
from django.templatetags.static import static
from django.utils.html import format_html


# ── Кастомная тема ────────────────────────────────────────────
@hooks.register("insert_global_admin_css")
def admin_custom_css():
    return format_html('<link rel="stylesheet" href="{}?v=2">', static("tours/admin_theme.css"))


# ── Убираем лишние панели с главной дашборда ──────────────────
@hooks.register("construct_homepage_panels")
def remove_homepage_panels(request, panels):
    keep = {"site_summary"}
    panels[:] = [p for p in panels if getattr(p, "name", None) in keep]


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
