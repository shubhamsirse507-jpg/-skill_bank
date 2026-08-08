"""
fix_bookings_schema.py
Run this once: python fix_bookings_schema.py
Adds ALL missing columns to bookings, exchange_requests, and other tables.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from django.db import connection

COLUMNS = {
    'bookings': [
        ('request_id',      'BIGINT NOT NULL DEFAULT 1'),
        ('scheduled_date',  'DATE NOT NULL DEFAULT "2026-01-01"'),
        ('start_time',      'TIME NOT NULL DEFAULT "09:00:00"'),
        ('end_time',        'TIME NOT NULL DEFAULT "10:00:00"'),
        ('meeting_mode',    'VARCHAR(10) NOT NULL DEFAULT "online"'),
        ('meeting_link',    'VARCHAR(500) NOT NULL DEFAULT ""'),
        ('status',          'VARCHAR(12) NOT NULL DEFAULT "scheduled"'),
        ('created_at',      'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ('updated_at',      'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    ],
    'exchange_requests': [
        ('requester_id',  'BIGINT'),
        ('receiver_id',   'BIGINT'),
        ('skill_id',      'BIGINT'),
        ('title',         'VARCHAR(200) NOT NULL DEFAULT "Skill Exchange"'),
        ('message',       'TEXT'),
        ('status',        'VARCHAR(12) NOT NULL DEFAULT "pending"'),
        ('created_at',    'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ('updated_at',    'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    ],
    'review_ratings': [
        ('booking_id',          'BIGINT'),
        ('reviewer_id',         'BIGINT'),
        ('reviewed_user_id',    'BIGINT'),
        ('rating',              'INT NOT NULL DEFAULT 5'),
        ('communication_rating','INT NOT NULL DEFAULT 5'),
        ('clarity_rating',      'INT NOT NULL DEFAULT 5'),
        ('punctuality_rating',  'INT NOT NULL DEFAULT 5'),
        ('comment',             'TEXT'),
        ('tags',                'VARCHAR(255) NOT NULL DEFAULT ""'),
        ('would_recommend',     'TINYINT(1) NOT NULL DEFAULT 1'),
        ('created_at',          'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
    ],
    'conversations': [
        ('exchange_id',  'BIGINT'),
        ('created_at',   'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ('updated_at',   'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    ],
    'messages': [
        ('conversation_id', 'BIGINT'),
        ('sender_id',       'BIGINT'),
        ('content',         'TEXT'),
        ('is_read',         'TINYINT(1) NOT NULL DEFAULT 0'),
        ('sent_at',         'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
    ],
    'notifications': [
        ('user_id',              'BIGINT'),
        ('title',                'VARCHAR(200) NOT NULL DEFAULT "Notification"'),
        ('message',              'TEXT'),
        ('notification_type',    'VARCHAR(50) NOT NULL DEFAULT "system"'),
        ('is_read',              'TINYINT(1) NOT NULL DEFAULT 0'),
        ('action_url',           'VARCHAR(255) NOT NULL DEFAULT ""'),
        ('action_text',          'VARCHAR(100) NOT NULL DEFAULT ""'),
        ('sender_name',          'VARCHAR(100) NOT NULL DEFAULT ""'),
        ('sender_avatar',        'VARCHAR(255) NOT NULL DEFAULT ""'),
        ('created_at',           'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
    ],
    'profiles_userprofile': [
        ('user_id',            'BIGINT UNIQUE'),
        ('phone',              'VARCHAR(20) NOT NULL DEFAULT ""'),
        ('headline',           'VARCHAR(200) NOT NULL DEFAULT ""'),
        ('bio',                'TEXT'),
        ('city',               'VARCHAR(100) NOT NULL DEFAULT ""'),
        ('country',            'VARCHAR(100) NOT NULL DEFAULT ""'),
        ('location',           'VARCHAR(150) NOT NULL DEFAULT ""'),
        ('work_preference',    'VARCHAR(50) NOT NULL DEFAULT "Remote"'),
        ('matching_goal',      'VARCHAR(100) NOT NULL DEFAULT "Peer Skill Swap"'),
        ('avatar_preset_url',  'VARCHAR(255) NOT NULL DEFAULT "https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero"'),
        ('show_email',         'TINYINT(1) NOT NULL DEFAULT 1'),
        ('show_phone',         'TINYINT(1) NOT NULL DEFAULT 0'),
        ('is_profile_public',  'TINYINT(1) NOT NULL DEFAULT 1'),
        ('experience_summary', 'TEXT'),
        ('availability',       'VARCHAR(20) NOT NULL DEFAULT "available"'),
    ],
    'skills': [
        ('title',         'VARCHAR(200) NOT NULL DEFAULT "Skill"'),
        ('description',   'TEXT'),
        ('demand_level',  'VARCHAR(10) NOT NULL DEFAULT "MEDIUM"'),
        ('is_featured',   'TINYINT(1) NOT NULL DEFAULT 0'),
        ('status',        'VARCHAR(10) NOT NULL DEFAULT "approved"'),
        ('skill_type',    'VARCHAR(10) NOT NULL DEFAULT "offered"'),
        ('level',         'VARCHAR(20) NOT NULL DEFAULT "Beginner"'),
        ('category_id',   'BIGINT'),
        ('user_id',       'BIGINT'),
        ('created_at',    'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ('updated_at',    'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    ],
}

def run():
    with connection.cursor() as cursor:
        existing_tables = connection.introspection.table_names()
        print(f"\n📋 Found {len(existing_tables)} tables in DB\n")

        for table, cols in COLUMNS.items():
            if table not in existing_tables:
                print(f"⏭️  Table '{table}' does not exist — skipping")
                continue

            print(f"\n🔧 Auditing table: {table}")
            for col_name, col_def in cols:
                cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", [col_name])
                exists = cursor.fetchone()
                if exists:
                    print(f"   ✓  '{col_name}' already exists")
                else:
                    try:
                        sql = f"ALTER TABLE `{table}` ADD COLUMN `{col_name}` {col_def}"
                        cursor.execute(sql)
                        print(f"   ✅ Added '{col_name}' ({col_def[:40]}...)")
                    except Exception as e:
                        print(f"   ⚠️  Error adding '{col_name}': {e}")

        print("\n\n✅ Schema repair complete!\n")


if __name__ == '__main__':
    run()
