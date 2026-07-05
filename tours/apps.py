from django.apps import AppConfig


class ToursConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tours"
    verbose_name = "Туры"

    def ready(self):
        from django.db.backends.signals import connection_created

        def set_wal(sender, connection, **kwargs):
            if connection.vendor == "sqlite":
                connection.cursor().execute("PRAGMA journal_mode=WAL;")
                connection.cursor().execute("PRAGMA synchronous=NORMAL;")

        connection_created.connect(set_wal)
