"""
Management command to delete proctoring snapshots older than PROCTOR_RETENTION_DAYS.
"""
import datetime
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from admin_panel.models import TestViolation


class Command(BaseCommand):
    help = "Delete proctoring snapshots older than PROCTOR_RETENTION_DAYS."

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=None,
                            help='Override PROCTOR_RETENTION_DAYS')

    def handle(self, *args, **options):
        days = options['days'] if options['days'] is not None else getattr(settings, 'PROCTOR_RETENTION_DAYS', 14)
        cutoff = timezone.now() - datetime.timedelta(days=days)
        private_root = Path(getattr(settings, 'PRIVATE_MEDIA_ROOT', settings.BASE_DIR / 'private_media'))

        expired = TestViolation.objects.filter(
            started_at__lt=cutoff
        ).exclude(snapshot_path='')

        deleted_files = 0
        cleared_rows = 0
        for v in expired:
            file_path = private_root / v.snapshot_path
            if file_path.exists() and file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_files += 1
                except OSError:
                    pass
            v.snapshot_path = ''
            v.save(update_fields=['snapshot_path'])
            cleared_rows += 1

        self.stdout.write(self.style.SUCCESS(
            f"Retention cleanup complete: {deleted_files} snapshot file(s) deleted, {cleared_rows} row(s) cleared (cutoff={days}d)."
        ))
