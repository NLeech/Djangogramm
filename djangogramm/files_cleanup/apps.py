from django.apps import AppConfig


class FilesCleanupConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'files_cleanup'

    def ready(self):
        super().ready()
        from . import signals
