from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    # ─── Importa las señales al iniciar ──────────────────────────
    def ready(self):
        # Importación perezosa para registrar los listeners
        import apps.users.signals  # noqa
