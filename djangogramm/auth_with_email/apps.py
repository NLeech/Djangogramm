from django.apps import AppConfig


class AuthWithEmailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_with_email'
    verbose_name = "Authentication"

    def ready(self):
        super().ready()
        from auth_with_email import signals
