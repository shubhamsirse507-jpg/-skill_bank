import os
import sys
from django.apps import AppConfig


class UserDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_dashboard'

    def ready(self):
        # Auto-run schema column repairs on server startup
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv or 'uwsgi' in sys.argv:
            try:
                from fix_missing_tables import fix_schema
                fix_schema()
            except Exception as e:
                print("Auto schema fix notice:", e)
