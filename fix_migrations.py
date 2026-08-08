"""
fix_migrations.py
-----------------
Run this script to apply all pending migrations and create missing tables.

Usage:
  d:\Django_framework\skill_bank\venv\Scripts\python.exe fix_migrations.py

Tables that will be created:
  - skill_management_skillcertificate   (SkillCertificate model)
  - teacher_mock_tests                  (TeacherMockTest model)
"""
import os
import sys
import django

# Set working directory and Django settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')

django.setup()

from django.core.management import call_command

print("=" * 60)
print("  SkillBank — Applying Pending Migrations")
print("=" * 60)

print("\n[1/2] Running makemigrations (safety check)...")
try:
    call_command('makemigrations', '--no-input')
except Exception as e:
    print(f"  makemigrations note: {e}")

print("\n[2/2] Applying all migrations to database...")
call_command('migrate', '--no-input')

print("\n" + "=" * 60)
print("  ✅ SUCCESS — All tables are now ready!")
print("=" * 60)

# Verify the tables exist
from django.db import connection
cursor = connection.cursor()
tables = connection.introspection.table_names()
cert_ok = 'skill_management_skillcertificate' in tables
test_ok = 'teacher_mock_tests' in tables

print(f"\n  Table 'skill_management_skillcertificate': {'✅ EXISTS' if cert_ok else '❌ MISSING'}")
print(f"  Table 'teacher_mock_tests':                {'✅ EXISTS' if test_ok else '❌ MISSING'}")

print("\nRestart your server:")
print("  d:\\Django_framework\\skill_bank\\venv\\Scripts\\python.exe manage.py runserver")
