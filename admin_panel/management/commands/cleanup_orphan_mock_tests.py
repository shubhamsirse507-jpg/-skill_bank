"""
Management command to clean up orphan PENDING TeacherMockTest rows
created by the old buggy GET /admin-panel/mock-test/ endpoint.
"""
from django.core.management.base import BaseCommand
from admin_panel.models import TeacherMockTest


class Command(BaseCommand):
    help = "Delete orphan PENDING TeacherMockTest rows that have no TeacherTestInvite."

    def handle(self, *args, **options):
        orphans = TeacherMockTest.objects.filter(status='PENDING', invite__isnull=True)
        count = orphans.count()
        orphans.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphan PENDING TeacherMockTest row(s)."))
