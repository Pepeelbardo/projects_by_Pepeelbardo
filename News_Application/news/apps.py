"""Application configuration for the news app."""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news"

    def ready(self):
        from . import signals  # noqa: F401
