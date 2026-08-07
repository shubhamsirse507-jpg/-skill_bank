from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_panel.models import SkillCategory, PlatformSkill, PlatformReport, PlatformNotice, AuditLog
from messaging.models import SkillExchange, Message
from ratings.models import ReviewRating
import random


class Command(BaseCommand):
    help = 'Seeds initial sample data for Admin Panel UI testing'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Admin Panel data...")

        # 1. Ensure sample users exist
        users = []
        user_data = [
            ("alex_dev", "alex@skillbank.io", "Alex", "Mercer"),
            ("sarah_design", "sarah@skillbank.io", "Sarah", "Jenkins"),
            ("chen_data", "chen@skillbank.io", "Wei", "Chen"),
            ("maria_mktg", "maria@skillbank.io", "Maria", "Garcia"),
            ("david_pm", "david@skillbank.io", "David", "Kim"),
        ]

        for username, email, first_name, last_name in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)

        # 2. Seed Categories & Skills
        cat_skills = [
            ("Development & Tech", "fa-solid fa-code", "Software engineering, web development & DevOps", [
                ("Python & Django", "HIGH"),
                ("React & Next.js", "HIGH"),
                ("TypeScript", "MEDIUM"),
                ("Docker & Kubernetes", "MEDIUM"),
            ]),
            ("Design & Creative", "fa-solid fa-paintbrush", "UI/UX design, motion graphics & branding", [
                ("Figma Design Systems", "HIGH"),
                ("User Research & Prototyping", "MEDIUM"),
                ("3D Blender Modeling", "LOW"),
            ]),
            ("Data & AI", "fa-solid fa-brain", "Data science, machine learning & analytics", [
                ("Machine Learning Models", "HIGH"),
                ("SQL & Data Engineering", "MEDIUM"),
                ("Prompt Engineering", "HIGH"),
            ]),
            ("Business & Marketing", "fa-solid fa-chart-line", "Growth marketing, strategy & project management", [
                ("Product Management", "HIGH"),
                ("SEO & Growth Hacking", "MEDIUM"),
            ]),
        ]

        for cat_name, icon, desc, skills_list in cat_skills:
            category, _ = SkillCategory.objects.get_or_create(
                name=cat_name,
                defaults={'icon_class': icon, 'description': desc}
            )
            for s_name, demand in skills_list:
                PlatformSkill.objects.get_or_create(
                    name=s_name,
                    category=category,
                    defaults={'demand_level': demand}
                )

        # 3. Seed Skill Exchanges if none exist
        if SkillExchange.objects.count() == 0 and len(users) >= 2:
            ex1 = SkillExchange.objects.create(
                requester=users[0],
                provider=users[1],
                title="Django REST API Architecture Masterclass",
                requested_skill="Figma Design Systems",
                offered_skill="Python & Django",
                status="COMPLETED"
            )
            Message.objects.create(
                exchange=ex1,
                sender=users[0],
                content="Hey Sarah! Looking forward to reviewing the REST endpoints."
            )
            Message.objects.create(
                exchange=ex1,
                sender=users[1],
                content="Awesome Alex! Let us kick off at 4 PM."
            )

            # Create review
            ReviewRating.objects.create(
                exchange=ex1,
                reviewer=users[0],
                reviewee=users[1],
                rating=5,
                communication_rating=5,
                clarity_rating=5,
                punctuality_rating=5,
                comment="Sarah provided an exceptional walkthrough of design tokens!",
                tags="Patient, Clear Communicator, Highly Skilled"
            )

        # 4. Seed Moderation Reports
        if PlatformReport.objects.count() == 0 and len(users) >= 3:
            PlatformReport.objects.create(
                reporter=users[2],
                reported_user=users[3],
                reason="SPAM",
                details="Sent irrelevant promotional links during our scheduled exchange session.",
                status="PENDING"
            )
            PlatformReport.objects.create(
                reporter=users[1],
                reported_user=users[4],
                reason="HARASSMENT",
                details="Unprofessional language used in messaging exchange chat.",
                status="IN_REVIEW",
                action_taken="Sent warning notice to user."
            )

        # 5. Seed Announcements
        if PlatformNotice.objects.count() == 0:
            PlatformNotice.objects.create(
                title="Welcome to SkillBank Platform 2.0",
                message="We have updated our real-time messaging engine and rating system!",
                priority="HIGH",
                target_group="ALL"
            )
            PlatformNotice.objects.create(
                title="Mentor Rewards Program Live",
                message="Top rated mentors with 5+ verified exchanges receive featured profile badges.",
                priority="MEDIUM",
                target_group="TEACHERS"
            )

        # 6. Seed Audit Log
        if AuditLog.objects.count() == 0:
            AuditLog.objects.create(
                actor=users[0] if users else None,
                action="Admin Panel initialized and verified.",
                target="System"
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Admin Panel sample data!"))
