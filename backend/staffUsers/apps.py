from django.apps import AppConfig


class StaffusersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staffUsers'

    def ready(self):
        from . import signals  # noqa
