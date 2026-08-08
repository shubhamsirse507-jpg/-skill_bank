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
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, default='', max_length=20)),
                ('role', models.CharField(choices=[('user', 'User'), ('admin', 'Admin')], default='user', max_length=10)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('blocked', 'Blocked')], default='active', max_length=20)),
                ('bio', models.TextField(blank=True, default='')),
                ('location', models.CharField(blank=True, default='', max_length=200)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_photos/')),
                ('availability', models.CharField(choices=[('available', 'Available'), ('busy', 'Busy'), ('weekends_only', 'Weekends Only'), ('not_available', 'Not Available')], default='available', max_length=20)),
                ('experience_summary', models.TextField(blank=True, default='')),
                ('headline', models.CharField(blank=True, default='', max_length=200)),
                ('city', models.CharField(blank=True, default='', max_length=100)),
                ('country', models.CharField(blank=True, default='', max_length=100)),
                ('work_preference', models.CharField(blank=True, default='Remote', max_length=50)),
                ('matching_goal', models.CharField(blank=True, default='Peer Skill Swap', max_length=100)),
                ('avatar_preset_url', models.URLField(blank=True, default='https://api.dicebear.com/7.x/avataaars/svg?seed=SkillHero')),
                ('show_email', models.BooleanField(default=True)),
                ('show_phone', models.BooleanField(default=False)),
                ('is_profile_public', models.BooleanField(default=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
                'db_table': 'user_profiles',
            },
        ),
    ]
