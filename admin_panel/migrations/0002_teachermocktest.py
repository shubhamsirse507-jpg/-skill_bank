import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherMockTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_name', models.CharField(max_length=150)),
                ('skill_level', models.CharField(default='Intermediate', max_length=50)),
                ('questions_json', models.JSONField(default=dict)),
                ('answers_json', models.JSONField(default=dict)),
                ('score', models.IntegerField(default=0)),
                ('total_questions', models.IntegerField(default=5)),
                ('percentage', models.FloatField(default=0.0)),
                ('status', models.CharField(
                    choices=[
                        ('PENDING', 'Pending Test'),
                        ('TAKEN', 'Test Taken - Awaiting Admin Review'),
                        ('APPROVED', 'Approved & Hired'),
                        ('REJECTED', 'Rejected'),
                    ],
                    default='PENDING',
                    max_length=20,
                )),
                ('admin_notes', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('teacher', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='mock_tests',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'teacher_mock_tests',
                'ordering': ['-created_at'],
            },
        ),
    ]
