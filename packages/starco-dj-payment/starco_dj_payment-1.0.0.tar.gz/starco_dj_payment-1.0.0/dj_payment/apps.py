from django.apps import AppConfig


class DjPaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dj_payment'

    def ready(self):
        from . import handlers