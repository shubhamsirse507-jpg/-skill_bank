import django.db.models.deletion
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformNotice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='MEDIUM', max_length=20)),
                ('target_group', models.CharField(choices=[('ALL', 'All Users'), ('TEACHERS', 'Mentors / Teachers'), ('LEARNERS', 'Learners')], default='ALL', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'platform_notices',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PlatformReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('SPAM', 'Spam or Unsolicited Promotion'), ('HARASSMENT', 'Harassment or Abusive Behavior'), ('FAKE_PROFILE', 'Fake Profile or Misrepresentation'), ('INAPPROPRIATE', 'Inappropriate Content'), ('OTHER', 'Other Violation')], default='OTHER', max_length=30)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending Review'), ('IN_REVIEW', 'Under Review'), ('RESOLVED', 'Resolved'), ('DISMISSED', 'Dismissed')], default='PENDING', max_length=20)),
                ('action_taken', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reported_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_reports', to=settings.AUTH_USER_MODEL)),
                ('reported_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports_against', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'reports',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=200)),
                ('target_table', models.CharField(blank=True, default='', max_length=100)),
                ('target_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'admin_logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
