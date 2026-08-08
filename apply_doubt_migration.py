import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from django.core.management import call_command

try:
    call_command('migrate', 'bookings')
    print("MIGRATE SUCCESSFUL!")
except Exception as e:
    print(f"MIGRATE ERROR: {e}")
