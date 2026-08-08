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

        # Comprehensive Column Audits & Auto-repair
        column_checks = {
            'bookings': [
                ('request_id', 'BIGINT'),
                ('scheduled_date', 'DATE'),
                ('start_time', 'TIME'),
                ('end_time', 'TIME'),
                ('meeting_mode', 'VARCHAR(10) DEFAULT "online"'),
                ('meeting_link', 'VARCHAR(255) DEFAULT ""'),
                ('status', 'VARCHAR(12) DEFAULT "scheduled"'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
            ],
            'exchange_requests': [
                ('requester_id', 'BIGINT'),
                ('receiver_id', 'BIGINT'),
                ('skill_id', 'BIGINT'),
                ('title', 'VARCHAR(200) DEFAULT "Skill Exchange"'),
                ('message', 'TEXT'),
                ('status', 'VARCHAR(12) DEFAULT "pending"'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
            ],
            'review_ratings': [
                ('booking_id', 'BIGINT'),
                ('reviewer_id', 'BIGINT'),
                ('reviewed_user_id', 'BIGINT'),
                ('rating', 'INT DEFAULT 5'),
                ('communication_rating', 'INT DEFAULT 5'),
                ('clarity_rating', 'INT DEFAULT 5'),
                ('punctuality_rating', 'INT DEFAULT 5'),
                ('comment', 'TEXT'),
                ('tags', 'VARCHAR(255) DEFAULT ""'),
                ('would_recommend', 'TINYINT(1) DEFAULT 1'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ],
            'skill_categories': [
                ('category_name', 'VARCHAR(100) DEFAULT "General"'),
                ('icon_class', 'VARCHAR(80) DEFAULT "fa-solid fa-layer-group"'),
                ('is_active', 'TINYINT(1) DEFAULT 1'),
                ('status', 'VARCHAR(10) DEFAULT "active"'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ],
            'skills': [
                ('title', 'VARCHAR(200) DEFAULT "Skill"'),
                ('description', 'TEXT'),
                ('demand_level', 'VARCHAR(10) DEFAULT "MEDIUM"'),
                ('is_featured', 'TINYINT(1) DEFAULT 0'),
                ('status', 'VARCHAR(10) DEFAULT "approved"'),
                ('skill_type', 'VARCHAR(10) DEFAULT "offered"'),
                ('level', 'VARCHAR(20) DEFAULT "Beginner"'),
                ('category_id', 'BIGINT'),
                ('user_id', 'BIGINT'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ],
            'notifications': [
                ('title', 'VARCHAR(200) DEFAULT "Notification"'),
                ('message', 'TEXT'),
                ('notification_type', 'VARCHAR(50) DEFAULT "system"'),
                ('is_read', 'TINYINT(1) DEFAULT 0'),
                ('action_url', 'VARCHAR(255) DEFAULT ""'),
                ('action_text', 'VARCHAR(100) DEFAULT ""'),
                ('sender_name', 'VARCHAR(100) DEFAULT ""'),
                ('sender_avatar', 'VARCHAR(255) DEFAULT ""'),
                ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP'),
            ],
            'profiles_userprofile': [
                ('phone', 'VARCHAR(20) DEFAULT ""'),
                ('headline', 'VARCHAR(200) DEFAULT ""'),
                ('bio', 'TEXT'),
                ('city', 'VARCHAR(100) DEFAULT ""'),
                ('country', 'VARCHAR(100) DEFAULT ""'),
                ('location', 'VARCHAR(150) DEFAULT ""'),
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
                                print(f"✅ Added missing column '{col_name}' to table '{table_name}'.")
                            except Exception as ex:
                                print(f"⚠️ Error adding column {col_name} to {table_name}: {ex}")

if __name__ == '__main__':
    fix_schema()
