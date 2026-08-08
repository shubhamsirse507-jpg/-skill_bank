import os
import django
from datetime import date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skill_bank.settings')
django.setup()

from fix_missing_tables import fix_schema
from django.contrib.auth.models import User
from profiles.models import UserProfile
from skill_management.models import SkillCategory, Skill
from messaging.models import SkillExchange, Conversation, Message
from bookings.models import Booking
from ratings.models import ReviewRating
from admin_panel.models import PlatformReport, PlatformNotice, AuditLog
from authentication.models import OTPVerification
from notifications.models import Notification

def setup_demo_accounts():
    print("Setting up Demo Test Accounts & Sample Conversations for Skill Bank...")
    fix_schema()

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

    skill_python, _ = Skill.objects.get_or_create(
        user=demo_user,
        title="Python & Django Web Development",
        defaults={'category': cat_code, 'level': 'Advanced', 'skill_type': 'offered', 'status': 'approved'}
    )

    skill_figma, _ = Skill.objects.get_or_create(
        user=teacher_user,
        title="UI/UX Prototyping in Figma",
        defaults={'category': cat_design, 'level': 'Intermediate', 'skill_type': 'offered', 'status': 'approved'}
    )

    # 5. Seed Sample Skill Exchanges, Conversations & Bookings
    exchange_accepted, _ = SkillExchange.objects.get_or_create(
        requester=demo_user,
        receiver=teacher_user,
        skill=skill_figma,
        defaults={
            'title': 'Figma for Python Swap',
            'message': 'Hi Sarah! I would love to learn Figma prototyping from you in exchange for Python lessons.',
            'status': 'accepted'
        }
    )

    conv_accepted, _ = Conversation.objects.get_or_create(
        request=exchange_accepted,
        defaults={'user_one': demo_user, 'user_two': teacher_user}
    )

    Message.objects.get_or_create(
        conversation=conv_accepted,
        sender=demo_user,
        message_text='Hi Sarah! Looking forward to our exchange session.'
    )
    Message.objects.get_or_create(
        conversation=conv_accepted,
        sender=teacher_user,
        message_text='Awesome Alex! Let us schedule our first session on Figma fundamentals.'
    )

    # Seed Booking session
    Booking.objects.get_or_create(
        request=exchange_accepted,
        defaults={
            'scheduled_date': date.today(),
            'start_time': time(15, 0),
            'end_time': time(16, 30),
            'meeting_mode': 'online',
            'meeting_link': 'https://meet.google.com/demo-skill-bank',
            'status': 'scheduled'
        }
    )

    # Seed Pending Request
    exchange_pending, _ = SkillExchange.objects.get_or_create(
        requester=teacher_user,
        receiver=demo_user,
        skill=skill_python,
        defaults={
            'title': 'Django Backend Mentorship',
            'message': 'Hey Alex! Could you guide me on Django REST API structure?',
            'status': 'pending'
        }
    )

    Conversation.objects.get_or_create(
        request=exchange_pending,
        defaults={'user_one': teacher_user, 'user_two': demo_user}
    )

    print("✅ Seeded Sample Exchange Requests, Conversations & Bookings!")
    print("=" * 60)
    print("DEMO ACCOUNTS READY FOR TESTING:")
    print("1) Student User  -> Username: demouser     | Password: DemoPassword123!")
    print("2) Teacher User  -> Username: demoteacher  | Password: TeacherPassword123!")
    print("3) Admin User    -> Username: admin        | Password: AdminPassword123!")
    print("=" * 60)

if __name__ == '__main__':
    setup_demo_accounts()
