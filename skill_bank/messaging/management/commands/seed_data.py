from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import SkillExchange, Message
from ratings.models import ReviewRating
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seeds initial sample users (Dnyani, Umair, Shubham), skill exchanges, chat messages, and ratings.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding demo data for Dnyani, Umair, and Shubham...'))

        # Create demo users: Dnyani, Umair, Shubham
        dnyani, _ = User.objects.get_or_create(
            username='dnyani',
            defaults={
                'first_name': 'Dnyani',
                'last_name': 'Patil',
                'email': 'dnyani@skillbank.io'
            }
        )
        dnyani.first_name = 'Dnyani'
        dnyani.last_name = 'Patil'
        dnyani.set_password('password123')
        dnyani.save()

        umair, _ = User.objects.get_or_create(
            username='umair',
            defaults={
                'first_name': 'Umair',
                'last_name': 'Khan',
                'email': 'umair@skillbank.io'
            }
        )
        umair.first_name = 'Umair'
        umair.last_name = 'Khan'
        umair.set_password('password123')
        umair.save()

        shubham, _ = User.objects.get_or_create(
            username='shubham',
            defaults={
                'first_name': 'Shubham',
                'last_name': 'Sharma',
                'email': 'shubham@skillbank.io'
            }
        )
        shubham.first_name = 'Shubham'
        shubham.last_name = 'Sharma'
        shubham.set_password('password123')
        shubham.save()

        # Clear existing data for clean slate
        SkillExchange.objects.all().delete()
        ReviewRating.objects.all().delete()

        # 1. Exchange: Dnyani & Umair (ACCEPTED - In Progress)
        ex1 = SkillExchange.objects.create(
            requester=dnyani,
            provider=umair,
            title='UI/UX Design for Python/Django REST Backend',
            requested_skill='Django REST Framework',
            offered_skill='UI/UX & Figma Design',
            status='ACCEPTED',
            scheduled_time=timezone.now() + timedelta(days=2)
        )

        Message.objects.create(
            exchange=ex1,
            sender=dnyani,
            content="Hi Umair! Excited for our session. I've uploaded the wireframe Figma links we discussed.",
            has_attachment=True,
            attachment_name="figma_design_tokens.pdf"
        )
        Message.objects.create(
            exchange=ex1,
            sender=umair,
            content="Hey Dnyani! Awesome design tokens. I've prepared our Django REST Framework project template and serializers guide."
        )
        Message.objects.create(
            exchange=ex1,
            sender=dnyani,
            content="Sounds perfect! Shall we schedule a 45-minute live screen share tomorrow at 4 PM UTC?"
        )
        Message.objects.create(
            exchange=ex1,
            sender=umair,
            content="4 PM UTC works great for me. See you then!"
        )

        # 2. Exchange: Dnyani & Shubham (COMPLETED)
        ex2 = SkillExchange.objects.create(
            requester=dnyani,
            provider=shubham,
            title='React Component Architecture for Machine Learning Dashboards',
            requested_skill='Data Science & ML',
            offered_skill='React & CSS Glassmorphism',
            status='COMPLETED'
        )

        Message.objects.create(
            exchange=ex2,
            sender=shubham,
            content="Thanks for guiding me through glassmorphism CSS components in React, Dnyani!"
        )
        Message.objects.create(
            exchange=ex2,
            sender=dnyani,
            content="My pleasure Shubham! Your breakdown of scikit-learn model evaluation was super clear."
        )

        ReviewRating.objects.create(
            exchange=ex2,
            reviewer=dnyani,
            reviewee=shubham,
            rating=5,
            communication_rating=5,
            clarity_rating=5,
            punctuality_rating=5,
            comment="Shubham is an exceptional teacher! He simplified complex ML concepts and helped me understand model metrics instantly.",
            tags="Expert Mentor, Great Communicator, Super Clear",
            would_recommend=True
        )

        ReviewRating.objects.create(
            exchange=ex2,
            reviewer=shubham,
            reviewee=dnyani,
            rating=5,
            communication_rating=5,
            clarity_rating=5,
            punctuality_rating=4,
            comment="Dnyani's design intuition is top notch! The UI components transformed our ML dashboard visual appeal.",
            tags="UI Genius, Highly Recommended, Patient",
            would_recommend=True
        )

        # 3. Exchange: Umair & Shubham (COMPLETED)
        ex3 = SkillExchange.objects.create(
            requester=umair,
            provider=shubham,
            title='PostgreSQL Query Optimization & System Design',
            requested_skill='System Design',
            offered_skill='PostgreSQL & Django ORM',
            status='COMPLETED'
        )

        ReviewRating.objects.create(
            exchange=ex3,
            reviewer=umair,
            reviewee=shubham,
            rating=5,
            communication_rating=5,
            clarity_rating=5,
            punctuality_rating=5,
            comment="Great system architecture session. Shubham gave clear code examples for backend scalability.",
            tags="Punctual, Clear Explanations, System Design Expert",
            would_recommend=True
        )

        # 4. Exchange: Shubham & Dnyani (REQUESTED)
        SkillExchange.objects.create(
            requester=shubham,
            provider=dnyani,
            title='Data Visualization with D3.js & Tailwind CSS',
            requested_skill='D3.js Visualization',
            offered_skill='Python Pandas Automation',
            status='REQUESTED'
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demo users Dnyani, Umair, and Shubham!'))
