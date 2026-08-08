import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skill_management', '0002_alter_skillcategory_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillCertificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate_id', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('skill_title', models.CharField(max_length=200)),
                ('category_name', models.CharField(blank=True, default='General', max_length=100)),
                ('grade_performance', models.CharField(default='Excellence (Passed)', max_length=50)),
                ('issue_date', models.DateField(auto_now_add=True)),
                ('remarks', models.TextField(blank=True, default='')),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='earned_certificates',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('teacher', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='issued_certificates',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-issue_date'],
            },
        ),
    ]
