"""
Data migration: delete orphan PENDING TeacherMockTest rows created by the old buggy GET endpoint.
"""
from django.db import migrations


def cleanup_orphan_pending(apps, schema_editor):
    TeacherMockTest = apps.get_model('admin_panel', 'TeacherMockTest')
    TeacherMockTest.objects.filter(status='PENDING', invite__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0003_teachermocktest_skill_and_more'),
    ]

    operations = [
        migrations.RunPython(cleanup_orphan_pending, migrations.RunPython.noop),
    ]
