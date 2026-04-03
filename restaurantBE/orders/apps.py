from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'restaurantBE.orders'

    def ready(self):
        import restaurantBE.orders.signals  # noqa: F401
