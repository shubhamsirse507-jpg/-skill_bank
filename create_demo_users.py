import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from profiles.models import UserProfile
from skill_management.models import SkillCategory, Skill
from messaging.models import SkillExchange
from bookings.models import Booking
from ratings.models import ReviewRating
from admin_panel.models import PlatformReport, PlatformNotice, AuditLog
from authentication.models import OTPVerification
from notifications.models import Notification

def ensure_tables_exist():
    with connection.schema_editor() as schema_editor:
        models = [
            UserProfile, SkillCategory, Skill, SkillExchange,
            Booking, ReviewRating, PlatformReport, PlatformNotice,
            AuditLog, OTPVerification, Notification
        ]
        existing_tables = connection.introspection.table_names()
        for model in models:
            table_name = model._meta.db_table
            if table_name not in existing_tables:
                try:
                    schema_editor.create_model(model)
                    print(f"Created missing table: {table_name}")
                except Exception as e:
                    pass

        # Table Column Upgrades for pre-existing SQL schema tables
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

def setup_demo_accounts():
    print("Setting up Demo Test Accounts for Skill Bank...")
    ensure_tables_exist()

    # 1. Demo Regular User
    demo_user, _ = User.objects.get_or_create(
        username='demouser',
        defaults={
            'email': 'demo@skillbank.com',
            'first_name': 'Alex',
            'last_name': 'Morgan',
            'is_active': True,
        }
    )
    demo_user.set_password('DemoPassword123!')
    demo_user.save()

    profile_user, _ = UserProfile.objects.get_or_create(user=demo_user)
    profile_user.headline = 'Passionate Python & Web Developer'
    profile_user.bio = 'Looking to learn Graphic Design and UI/UX in exchange for Python lessons!'
    profile_user.status = 'active'
    profile_user.role = 'user'
    profile_user.save()

    print("✅ Created/Reset Demo User: demouser / DemoPassword123!")

    # 2. Demo Teacher User
    teacher_user, _ = User.objects.get_or_create(
        username='demoteacher',
        defaults={
            'email': 'teacher@skillbank.com',
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'is_active': True,
        }
    )
    teacher_user.set_password('TeacherPassword123!')
    teacher_user.save()

    profile_teacher, _ = UserProfile.objects.get_or_create(user=teacher_user)
    profile_teacher.headline = 'Senior UI/UX & Graphic Designer'
    profile_teacher.bio = 'Teaching Adobe Illustrator & Figma prototyping!'
    profile_teacher.status = 'active'
    profile_teacher.role = 'user'
    profile_teacher.save()

    print("✅ Created/Reset Demo Teacher: demoteacher / TeacherPassword123!")

    # 3. Demo Admin User
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@skillbank.com',
            'first_name': 'System',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.set_password('AdminPassword123!')
    admin_user.save()

    profile_admin, _ = UserProfile.objects.get_or_create(user=admin_user)
    profile_admin.status = 'active'
    profile_admin.role = 'admin'
    profile_admin.save()

    print("✅ Created/Reset Demo Admin: admin / AdminPassword123!")

    # 4. Seed categories & skills
    cat_code, _ = SkillCategory.objects.get_or_create(category_name="Coding & IT", defaults={'icon_class': 'fa-solid fa-code'})
    cat_design, _ = SkillCategory.objects.get_or_create(category_name="Design & Arts", defaults={'icon_class': 'fa-solid fa-palette'})
    cat_music, _ = SkillCategory.objects.get_or_create(category_name="Music & Audio", defaults={'icon_class': 'fa-solid fa-music'})

    Skill.objects.get_or_create(
        user=demo_user,
        title="Python & Django Web Development",
        defaults={'category': cat_code, 'level': 'Advanced', 'skill_type': 'offered', 'status': 'approved'}
    )

    Skill.objects.get_or_create(
        user=teacher_user,
        title="UI/UX Prototyping in Figma",
        defaults={'category': cat_design, 'level': 'Intermediate', 'skill_type': 'offered', 'status': 'approved'}
    )

    print("=" * 60)
    print("DEMO ACCOUNTS READY FOR TESTING:")
    print("1) Student User  -> Username: demouser     | Password: DemoPassword123!")
    print("2) Teacher User  -> Username: demoteacher  | Password: TeacherPassword123!")
    print("3) Admin User    -> Username: admin        | Password: AdminPassword123!")
    print("=" * 60)

if __name__ == '__main__':
    setup_demo_accounts()
