from django.apps import AppConfig

class AccountsConfig(AppConfig):
    def ready(self):
        # Import signals only when Django is ready
        from . import imgbb_signals
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
