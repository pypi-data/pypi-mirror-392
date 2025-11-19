from django.apps import AppConfig


class LogViewerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "logviewer"
    verbose_name = "LogViewer"

    def ready(self):
        from . import site  # noqa: F401
