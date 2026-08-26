import os
import django
from django.db import connection


def fix_schema():
    """
    Database-agnostic schema checker and auto-repair.
    Works on SQLite, PostgreSQL, and MySQL.
    """
    print("Checking and creating any missing database tables & columns...")
    try:
        from profiles.models import UserProfile
        from skill_management.models import SkillCategory, Skill, SkillCertificate
        from messaging.models import SkillExchange, Message, Conversation
        from bookings.models import Booking, Batch, BatchEnrollment, DoubtCall
        from ratings.models import ReviewRating
        from admin_panel.models import PlatformReport, PlatformNotice, AuditLog, TeacherMockTest
        from authentication.models import OTPVerification
        from notifications.models import Notification
        from payments.models import Wallet, WalletTransaction, PaymentReceipt

        with connection.schema_editor() as schema_editor:
            models = [
                UserProfile, SkillCategory, Skill, SkillCertificate,
                SkillExchange, Message, Conversation,
                Booking, Batch, BatchEnrollment, DoubtCall,
                ReviewRating, PlatformReport, PlatformNotice, AuditLog,
                TeacherMockTest, OTPVerification, Notification,
                Wallet, WalletTransaction, PaymentReceipt,
            ]

            existing_tables = connection.introspection.table_names()

            for model in models:
                table_name = model._meta.db_table
                if table_name not in existing_tables:
                    print(f"Creating missing table: {table_name}")
                    try:
                        schema_editor.create_model(model)
                        print(f"✅ Successfully created table {table_name}")
                    except Exception as e:
                        print(f"⚠️ Error creating {table_name}: {e}")

            # Detect database vendor for syntax differences
            db_vendor = connection.vendor  # 'sqlite', 'postgresql', 'mysql'

            def safe_default(value, col_type):
                """Return a SQL DEFAULT clause that works on both SQLite and PostgreSQL."""
                # PostgreSQL uses single-quotes for string literals; SQLite accepts both.
                # Omit DEFAULT for PostgreSQL for non-string types to avoid syntax errors.
                if db_vendor == 'postgresql':
                    # For PostgreSQL just return the type without a DEFAULT to avoid
                    # ALTER TABLE issues — Django migrations handle defaults properly.
                    return col_type
                # SQLite: include DEFAULT with single-quoted strings
                return f"{col_type} DEFAULT '{value}'"

            # Column checks — use single quotes (PostgreSQL-safe)
            column_checks = {
                'bookings': [
                    ('request_id', 'BIGINT'),
                    ('scheduled_date', 'DATE'),
                    ('start_time', 'TIME'),
                    ('end_time', 'TIME'),
                    ('meeting_mode', safe_default('online', 'VARCHAR(10)')),
                    ('meeting_link', safe_default('', 'VARCHAR(255)')),
                    ('status', safe_default('scheduled', 'VARCHAR(12)')),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ],
                'exchange_requests': [
                    ('requester_id', 'BIGINT'),
                    ('receiver_id', 'BIGINT'),
                    ('skill_id', 'BIGINT'),
                    ('title', safe_default('Skill Exchange', 'VARCHAR(200)')),
                    ('message', 'TEXT'),
                    ('status', safe_default('pending', 'VARCHAR(12)')),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
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
                    ('tags', safe_default('', 'VARCHAR(255)')),
                    ('would_recommend', 'BOOLEAN DEFAULT TRUE'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ],
                'skill_categories': [
                    ('category_name', safe_default('General', 'VARCHAR(100)')),
                    ('icon_class', safe_default('fa-solid fa-layer-group', 'VARCHAR(80)')),
                    ('is_active', 'BOOLEAN DEFAULT TRUE'),
                    ('status', safe_default('active', 'VARCHAR(10)')),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ],
                'skills': [
                    ('title', safe_default('Skill', 'VARCHAR(200)')),
                    ('description', 'TEXT'),
                    ('demand_level', safe_default('MEDIUM', 'VARCHAR(10)')),
                    ('is_featured', 'BOOLEAN DEFAULT FALSE'),
                    ('status', safe_default('approved', 'VARCHAR(10)')),
                    ('skill_type', safe_default('offered', 'VARCHAR(10)')),
                    ('level', safe_default('Beginner', 'VARCHAR(20)')),
                    ('category_id', 'BIGINT'),
                    ('user_id', 'BIGINT'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ],
                'notifications': [
                    ('title', safe_default('Notification', 'VARCHAR(200)')),
                    ('message', 'TEXT'),
                    # Correct column name is 'type' (NOT 'notification_type') per the model
                    ('type', safe_default('system', 'VARCHAR(30)')),
                    ('is_read', 'BOOLEAN DEFAULT FALSE'),
                    ('action_url', safe_default('', 'VARCHAR(255)')),
                    ('action_text', safe_default('', 'VARCHAR(100)')),
                    ('sender_name', safe_default('', 'VARCHAR(100)')),
                    ('sender_avatar', safe_default('', 'VARCHAR(255)')),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ],
                'profiles_userprofile': [
                    ('phone', safe_default('', 'VARCHAR(20)')),
                    ('headline', safe_default('', 'VARCHAR(200)')),
                    ('bio', 'TEXT'),
                    ('city', safe_default('', 'VARCHAR(100)')),
                    ('country', safe_default('', 'VARCHAR(100)')),
                    ('location', safe_default('', 'VARCHAR(150)')),
                    ('work_preference', safe_default('Remote', 'VARCHAR(50)')),
                    ('matching_goal', safe_default('Peer Skill Swap', 'VARCHAR(100)')),
                    ('avatar_preset_url', safe_default('https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero', 'VARCHAR(255)')),
                    ('show_email', 'BOOLEAN DEFAULT TRUE'),
                    ('show_phone', 'BOOLEAN DEFAULT FALSE'),
                    ('is_profile_public', 'BOOLEAN DEFAULT TRUE'),
                    ('availability', safe_default('available', 'VARCHAR(20)')),
                    ('two_factor_enabled', 'BOOLEAN DEFAULT TRUE'),
                ],
            }

            with connection.cursor() as cursor:
                for table_name, cols in column_checks.items():
                    if table_name in existing_tables:
                        try:
                            desc = connection.introspection.get_table_description(cursor, table_name)
                            existing_col_names = [col.name.lower() for col in desc]
                            for col_name, col_def in cols:
                                if col_name.lower() not in existing_col_names:
                                    try:
                                        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                                        print(f"✅ Added missing column '{col_name}' to table '{table_name}'.")
                                    except Exception as ex:
                                        print(f"⚠️ Notice adding column {col_name} to {table_name}: {ex}")
                        except Exception as t_err:
                            print(f"⚠️ Inspection notice for {table_name}: {t_err}")
    except Exception as general_err:
        print(f"⚠️ fix_schema notice: {general_err}")


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
    django.setup()
    fix_schema()
