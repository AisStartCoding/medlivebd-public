from django.apps import AppConfig


class BackendConfig(AppConfig):
    name = "backend"
    label = "medlive"
    verbose_name = "MedLiveBD API"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        # The loaders that make values arrive as the Node driver gave them.
        from backend.core.database import connection as db
