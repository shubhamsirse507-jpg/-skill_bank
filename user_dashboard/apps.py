from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UserDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_dashboard'

    def ready(self):
        def on_post_migrate(sender, **kwargs):
            try:
                from fix_missing_tables import fix_schema
                fix_schema()
            except Exception:
                pass

        post_migrate.connect(on_post_migrate, sender=self)
