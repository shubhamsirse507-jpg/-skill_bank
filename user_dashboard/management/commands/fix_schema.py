"""
Django management command: fix_schema
Usage: python manage.py fix_schema
Adds all missing columns to MySQL tables AND fixes broken FK constraints
that point to wrong tables (e.g., skills.user_id -> users vs auth_user).
"""
from django.core.management.base import BaseCommand
from django.db import connection


# All columns that must exist in each table
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
        ('booking_id',            'BIGINT'),
        ('reviewer_id',           'BIGINT'),
        ('reviewed_user_id',      'BIGINT'),
        ('rating',                'INT NOT NULL DEFAULT 5'),
        ('communication_rating',  'INT NOT NULL DEFAULT 5'),
        ('clarity_rating',        'INT NOT NULL DEFAULT 5'),
        ('punctuality_rating',    'INT NOT NULL DEFAULT 5'),
        ('comment',               'TEXT'),
        ('tags',                  'VARCHAR(255) NOT NULL DEFAULT ""'),
        ('would_recommend',       'TINYINT(1) NOT NULL DEFAULT 1'),
        ('created_at',            'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
    ],
    'conversations': [
        ('exchange_id',  'BIGINT'),
        ('user_one_id',  'BIGINT'),
        ('user_two_id',  'BIGINT'),
        ('created_at',   'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ('updated_at',   'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
    ],
    'messages': [
        ('conversation_id', 'BIGINT'),
        ('sender_id',       'BIGINT'),
        ('message_text',    'TEXT'),
        ('is_read',         'TINYINT(1) NOT NULL DEFAULT 0'),
        ('sent_at',         'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
        ('created_at',      'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
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
        ('avatar_preset_url',  'VARCHAR(500) NOT NULL DEFAULT "https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero"'),
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
    'skill_categories': [
        ('category_name', 'VARCHAR(100) NOT NULL DEFAULT "General"'),
        ('icon_class',    'VARCHAR(80) NOT NULL DEFAULT "fa-solid fa-layer-group"'),
        ('is_active',     'TINYINT(1) NOT NULL DEFAULT 1'),
        ('status',        'VARCHAR(10) NOT NULL DEFAULT "active"'),
        ('created_at',    'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'),
    ],
}

# FK constraints to fix: (table, column, bad_ref_table, good_ref_table, good_ref_col)
FK_FIXES = [
    # skills.user_id originally pointed to old `users` table, must point to auth_user
    ('skills',            'user_id',      'users',    'auth_user', 'id'),
    # skills.category_id may point to old `categories` table, must point to skill_categories
    ('skills',            'category_id',  'categories', 'skill_categories', 'id'),
    # exchange_requests FKs
    ('exchange_requests', 'requester_id', 'users',    'auth_user', 'id'),
    ('exchange_requests', 'receiver_id',  'users',    'auth_user', 'id'),
    # bookings FK
    ('bookings',          'request_id',   'sessions', 'exchange_requests', 'id'),
    # notifications FK
    ('notifications',     'user_id',      'users',    'auth_user', 'id'),
]


def get_fk_constraints(cursor, table, db_name):
    """Return list of (constraint_name, column_name, ref_table) for a table."""
    cursor.execute("""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """, [db_name, table])
    return cursor.fetchall()


class Command(BaseCommand):
    help = 'Fixes missing DB columns AND broken FK constraints for all Skill Bank tables'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🔧 Skill Bank Schema Repair Tool\n'))

        with connection.cursor() as cursor:
            # Get current database name
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            self.stdout.write(f'📦 Database: {db_name}\n')

            existing_tables = connection.introspection.table_names()
            self.stdout.write(f'📋 Found {len(existing_tables)} tables\n')

            # ── PHASE 1: Fix broken FK constraints ────────────────────────────
            self.stdout.write(self.style.MIGRATE_HEADING('\n── Phase 1: FK Constraint Repair ──\n'))
            for table, col, bad_ref, good_ref, good_col in FK_FIXES:
                if table not in existing_tables:
                    continue
                if good_ref not in existing_tables:
                    self.stdout.write(
                        self.style.WARNING(f'  ⏭️  Target table "{good_ref}" missing, skip FK fix for {table}.{col}')
                    )
                    continue

                constraints = get_fk_constraints(cursor, table, db_name)
                for constraint_name, column_name, ref_table in constraints:
                    if column_name == col and ref_table == bad_ref:
                        try:
                            # Drop bad FK
                            cursor.execute(
                                f"ALTER TABLE `{table}` DROP FOREIGN KEY `{constraint_name}`"
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✅ Dropped bad FK: {table}.{col} → {bad_ref} (was: {constraint_name})'
                                )
                            )
                            # Optionally add correct FK (only if col exists)
                            cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE '{col}'")
                            if cursor.fetchone():
                                new_fk_name = f"fk_{table}_{col}_fixed"
                                try:
                                    cursor.execute(
                                        f"ALTER TABLE `{table}` ADD CONSTRAINT `{new_fk_name}` "
                                        f"FOREIGN KEY (`{col}`) REFERENCES `{good_ref}`(`{good_col}`) "
                                        f"ON DELETE CASCADE"
                                    )
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f'  ✅ Added correct FK: {table}.{col} → {good_ref}.{good_col}'
                                        )
                                    )
                                except Exception as fk_err:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f'  ⚠️  Could not add new FK (data may be orphaned): {fk_err}'
                                        )
                                    )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ❌ Error fixing FK {constraint_name}: {e}')
                            )

            # ── PHASE 2: Add missing columns ──────────────────────────────────
            self.stdout.write(self.style.MIGRATE_HEADING('\n── Phase 2: Missing Column Repair ──\n'))
            added = 0
            skipped = 0
            errors = 0

            for table, cols in COLUMNS.items():
                if table not in existing_tables:
                    self.stdout.write(
                        self.style.WARNING(f'  ⏭️  Table "{table}" does not exist — skipping')
                    )
                    continue

                self.stdout.write(f'\n  🔍 Auditing: {table}')
                for col_name, col_def in cols:
                    cursor.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", [col_name])
                    if cursor.fetchone():
                        skipped += 1
                    else:
                        try:
                            cursor.execute(
                                f"ALTER TABLE `{table}` ADD COLUMN `{col_name}` {col_def}"
                            )
                            self.stdout.write(
                                self.style.SUCCESS(f'     ✅ Added "{col_name}"')
                            )
                            added += 1
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'     ❌ Error adding "{col_name}": {e}')
                            )
                            errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Done! Added {added} columns, {skipped} already existed, {errors} errors.\n'
            )
        )
