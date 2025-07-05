from django.apps import AppConfig

class MessagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messages"        # ruta en el proyecto
    label = "pipa_messages"       # ← NUEVO, evita colisión
    verbose_name = "Mensajes internos"
