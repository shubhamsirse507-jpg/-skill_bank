import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from django.db import connection
from profiles.models import UserProfile
from skill_management.models import SkillCategory, Skill
from messaging.models import SkillExchange, Message, Conversation
from bookings.models import Booking
from ratings.models import ReviewRating
from admin_panel.models import PlatformReport, PlatformNotice, AuditLog
from authentication.models import OTPVerification
from notifications.models import Notification

def fix_schema():
    print("Checking and creating any missing database tables & columns...")
    with connection.schema_editor() as schema_editor:
        models = [
            UserProfile, SkillCategory, Skill, SkillExchange,
            Message, Conversation, Booking, ReviewRating,
            PlatformReport, PlatformNotice, AuditLog,
            OTPVerification, Notification
        ]

        existing_tables = connection.introspection.table_names()
        print("Existing DB Tables:", existing_tables)

        for model in models:
            table_name = model._meta.db_table
            if table_name not in existing_tables:
                print(f"Creating missing table: {table_name}")
                try:
                    schema_editor.create_model(model)
                    print(f"✅ Successfully created table {table_name}")
                except Exception as e:
                    print(f"⚠️ Error creating {table_name}: {e}")

        # Table Column Upgrades
        column_checks = {
            'skill_categories': [
                ('icon_class', 'VARCHAR(80) DEFAULT "fa-solid fa-layer-group"'),
                ('is_active', 'TINYINT(1) DEFAULT 1'),
                ('status', 'VARCHAR(10) DEFAULT "active"'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ],
            'skills': [
                ('demand_level', 'VARCHAR(10) DEFAULT "MEDIUM"'),
                ('is_featured', 'TINYINT(1) DEFAULT 0'),
                ('status', 'VARCHAR(10) DEFAULT "approved"'),
                ('skill_type', 'VARCHAR(10) DEFAULT "offered"'),
                ('level', 'VARCHAR(20) DEFAULT "Beginner"'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ],
            'notifications': [
                ('action_url', 'VARCHAR(255) DEFAULT ""'),
                ('action_text', 'VARCHAR(100) DEFAULT ""'),
                ('sender_name', 'VARCHAR(100) DEFAULT ""'),
                ('sender_avatar', 'VARCHAR(255) DEFAULT ""'),
            ],
            'profiles_userprofile': [
                ('headline', 'VARCHAR(200) DEFAULT ""'),
                ('city', 'VARCHAR(100) DEFAULT ""'),
                ('country', 'VARCHAR(100) DEFAULT ""'),
                ('work_preference', 'VARCHAR(50) DEFAULT "Remote"'),
                ('matching_goal', 'VARCHAR(100) DEFAULT "Peer Skill Swap"'),
                ('avatar_preset_url', 'VARCHAR(255) DEFAULT "https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero"'),
                ('show_email', 'TINYINT(1) DEFAULT 1'),
                ('show_phone', 'TINYINT(1) DEFAULT 0'),
                ('is_profile_public', 'TINYINT(1) DEFAULT 1'),
                ('experience_summary', 'TEXT'),
                ('availability', 'VARCHAR(20) DEFAULT "available"'),
            ]
        }

        with connection.cursor() as cursor:
            for table_name, cols in column_checks.items():
                if table_name in existing_tables:
                    for col_name, col_def in cols:
                        cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{col_name}'")
                        if not cursor.fetchone():
                            try:
                                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                                print(f"Added missing column '{col_name}' to table '{table_name}'.")
                            except Exception as ex:
                                pass

if __name__ == '__main__':
    fix_schema()
