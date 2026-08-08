"""
management/commands/seed_dummy_users.py

Creates 3 dummy accounts in the SQLite database:
  1. student_user  — regular user (role: user)
  2. teacher_demo  — teacher / skill provider (role: user, is_staff: False)
  3. admin_demo    — platform admin (role: admin, is_staff: True, is_superuser: True)

Run:
    python manage.py seed_dummy_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import UserProfile
from skill_management.models import Skill, SkillCategory


# ── Dummy data ──────────────────────────────────────────────────────────────

USERS = [
    {
        "username": "student_user",
        "email": "student@skillbank.com",
        "password": "Student@1234",
        "first_name": "Ananya",
        "last_name": "Sharma",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "role": "user",
            "status": "active",
            "bio": "Passionate learner who loves Python, data science, and art.",
            "location": "Mumbai, India",
            "headline": "Student | Python Enthusiast | Aspiring Data Scientist",
            "city": "Mumbai",
            "country": "India",
            "phone": "+91-9876543210",
            "availability": "available",
            "work_preference": "Remote",
            "matching_goal": "Peer Skill Swap",
            "experience_summary": "2 years of self-taught programming. Looking to swap skills.",
            "avatar_preset_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ananya",
        },
    },
    {
        "username": "teacher_demo",
        "email": "teacher@skillbank.com",
        "password": "Teacher@1234",
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "is_staff": False,
        "is_superuser": False,
        "profile": {
            "role": "user",
            "status": "active",
            "bio": "Experienced software engineer with 8+ years teaching web development and Python.",
            "location": "Bangalore, India",
            "headline": "Senior Developer | Full-Stack Teacher | Open Source Contributor",
            "city": "Bangalore",
            "country": "India",
            "phone": "+91-9123456789",
            "availability": "weekends_only",
            "work_preference": "Hybrid",
            "matching_goal": "Mentor Students",
            "experience_summary": "8 years in Django, React, and cloud technologies. Love to teach.",
            "avatar_preset_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rajesh",
        },
    },
    {
        "username": "admin_demo",
        "email": "admin@skillbank.com",
        "password": "Admin@1234",
        "first_name": "Priya",
        "last_name": "Mehta",
        "is_staff": True,
        "is_superuser": True,
        "profile": {
            "role": "admin",
            "status": "active",
            "bio": "Platform administrator ensuring quality and smooth experience for all users.",
            "location": "Delhi, India",
            "headline": "Platform Admin | SkillBank Operations",
            "city": "Delhi",
            "country": "India",
            "phone": "+91-9001122334",
            "availability": "available",
            "work_preference": "Remote",
            "matching_goal": "Platform Growth",
            "experience_summary": "Managing SkillBank since inception. Oversees skill approvals and user support.",
            "avatar_preset_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Priya",
        },
    },
]

# Sample skill categories and skills to seed
CATEGORIES = [
    {"category_name": "Programming", "description": "Software development and coding skills", "icon_class": "fa-solid fa-code"},
    {"category_name": "Design",      "description": "UI/UX and graphic design skills",        "icon_class": "fa-solid fa-pen-nib"},
    {"category_name": "Music",       "description": "Musical instruments and theory",          "icon_class": "fa-solid fa-music"},
    {"category_name": "Language",    "description": "Spoken and written languages",            "icon_class": "fa-solid fa-language"},
]

SKILLS_BY_USER = {
    "student_user": [
        {"title": "Python Basics", "category": "Programming", "skill_type": "offered",
         "level": "Intermediate", "description": "I can teach Python fundamentals, loops, functions, and OOP.", "status": "approved"},
        {"title": "Guitar Lessons", "category": "Music",       "skill_type": "offered",
         "level": "Beginner",      "description": "Acoustic guitar basics — chords, strumming patterns.", "status": "approved"},
        {"title": "Web Design",    "category": "Design",       "skill_type": "wanted",
         "level": "Beginner",      "description": "I want to learn Figma and UI/UX principles.", "status": "approved"},
    ],
    "teacher_demo": [
        {"title": "Django Web Development", "category": "Programming", "skill_type": "offered",
         "level": "Advanced",     "description": "Full Django course: models, views, REST APIs, deployment.", "status": "approved", "is_featured": True},
        {"title": "React.js Frontend",      "category": "Programming", "skill_type": "offered",
         "level": "Advanced",     "description": "Modern React with hooks, context, and Redux.", "status": "approved", "is_featured": True},
        {"title": "Spanish Language",       "category": "Language",    "skill_type": "wanted",
         "level": "Beginner",     "description": "Would love to learn conversational Spanish.", "status": "approved"},
    ],
    "admin_demo": [
        {"title": "Project Management", "category": "Programming", "skill_type": "offered",
         "level": "Advanced",     "description": "Agile, Scrum, and platform operations management.", "status": "approved"},
    ],
}


# ── Command ──────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed the database with dummy users: student, teacher, and admin."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n🌱  Seeding dummy users into SQLite DB...\n"))

        # ── 1. Create Skill Categories ───────────────────────────────────────
        self.stdout.write("📂  Creating skill categories...")
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = SkillCategory.objects.get_or_create(
                category_name=cat_data["category_name"],
                defaults={
                    "description": cat_data["description"],
                    "icon_class":  cat_data["icon_class"],
                    "status":      "active",
                    "is_active":   True,
                }
            )
            cat_map[cat.category_name] = cat
            label = "Created" if created else "Already exists"
            self.stdout.write(f"   [{label}] {cat.category_name}")

        # ── 2. Create Users + Profiles ───────────────────────────────────────
        self.stdout.write("\n👤  Creating users and profiles...")
        for user_data in USERS:
            profile_data = user_data.pop("profile")

            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email":        user_data["email"],
                    "first_name":   user_data["first_name"],
                    "last_name":    user_data["last_name"],
                    "is_staff":     user_data["is_staff"],
                    "is_superuser": user_data["is_superuser"],
                    "is_active":    True,
                }
            )

            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"   [Created] {user.username}  (password: {user_data['password']})"))
            else:
                self.stdout.write(f"   [Exists]  {user.username}")

            # Create or update Wallet
            from payments.models import Wallet, WalletTransaction
            wallet, _ = Wallet.objects.get_or_create(user=user, defaults={'balance': 500.00 if user.username == 'teacher_demo' else 250.00})
            if not wallet.transactions.exists():
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=wallet.balance,
                    transaction_type='credit',
                    description='Welcome Bonus Credits'
                )

        # ── 4. Seed Group Batches ───────────────────────────────────────────
        self.stdout.write("\n🎓  Creating scheduled group batches...")
        from bookings.models import Batch, DoubtCall
        from django.utils import timezone
        import datetime

        teacher = User.objects.get(username='teacher_demo')
        prog_cat = cat_map.get('Programming')
        design_cat = cat_map.get('Design')

        if prog_cat:
            b1, b1_created = Batch.objects.get_or_create(
                title='Mastering Django REST Framework & WebSockets',
                defaults={
                    'instructor': teacher,
                    'category': prog_cat,
                    'description': 'A 2-hour intensive group class building real-time APIs and live chat rooms.',
                    'scheduled_at': timezone.now() + datetime.timedelta(days=2, hours=4),
                    'duration_minutes': 120,
                    'max_seats': 12,
                    'enrolled_count': 3,
                    'price_credits': 150.00,
                }
            )
            label = "Created" if b1_created else "Exists"
            self.stdout.write(f"   [{label}] Batch: {b1.title}")

        if design_cat:
            b2, b2_created = Batch.objects.get_or_create(
                title='UI/UX Design Systems in Figma for Beginners',
                defaults={
                    'instructor': teacher,
                    'category': design_cat,
                    'description': 'Learn color theory, auto-layout, components, and interactive prototypes.',
                    'scheduled_at': timezone.now() + datetime.timedelta(days=4, hours=2),
                    'duration_minutes': 90,
                    'max_seats': 15,
                    'enrolled_count': 5,
                    'price_credits': 100.00,
                }
            )
            label = "Created" if b2_created else "Exists"
            self.stdout.write(f"   [{label}] Batch: {b2.title}")

        # ── 5. Seed Instant Doubt Calls ─────────────────────────────────────
        self.stdout.write("\n⚡  Creating sample instant doubt calls...")
        student = User.objects.get(username='student_user')
        d1, d1_created = DoubtCall.objects.get_or_create(
            subject='Django Foreign Key Migration Error',
            defaults={
                'learner': student,
                'mentor': teacher,
                'question': 'How do I resolve OperationalError during SQLite migration with existing table records?',
                'status': 'searching',
                'meeting_link': 'https://meet.jit.si/SkillBankDoubt-DjangoFK'
            }
        )
        label = "Created" if d1_created else "Exists"
        self.stdout.write(f"   [{label}] Doubt: {d1.subject}")


        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("  Dummy data seeded successfully!"))
        self.stdout.write(self.style.SUCCESS(""))
        self.stdout.write(self.style.SUCCESS("  Login Credentials:"))
        self.stdout.write(self.style.SUCCESS("  Student  -> username: student_user  | password: Student@1234"))
        self.stdout.write(self.style.SUCCESS("  Teacher  -> username: teacher_demo  | password: Teacher@1234"))
        self.stdout.write(self.style.SUCCESS("  Admin    -> username: admin_demo    | password: Admin@1234"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write("  Django Admin : http://127.0.0.1:8000/admin/")
        self.stdout.write("  SQLite file  : d:/Django_framework/skill_bank/db.sqlite3")
        self.stdout.write("")
