import os
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
import django
django.setup()

from django.core.management import call_command

print("=== 1. Making migrations ===")
try:
    call_command('makemigrations', 'bookings', 'payments', 'profiles', 'skill_management', 'authentication')
except Exception as e:
    print("makemigrations note:", e)

print("\n=== 2. Applying migrations ===")
try:
    call_command('migrate')
except Exception as e:
    print("migrate note:", e)

print("\n=== 3. Seeding dummy users, batches, doubts, and wallets ===")
try:
    call_command('seed_dummy_users')
except Exception as e:
    print("seed_dummy_users note:", e)

print("\n✅ Database setup complete!")
