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
            name='SkillCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('description', models.TextField(blank=True, default='')),
                ('icon', models.CharField(blank=True, default='code', max_length=50)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Skill Categories',
                'db_table': 'skill_categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, default='')),
                ('level', models.CharField(choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced'), ('Expert', 'Expert')], default='Beginner', max_length=20)),
                ('skill_type', models.CharField(choices=[('offered', 'Skill Offered'), ('wanted', 'Skill Wanted')], default='offered', max_length=10)),
                ('experience_years', models.PositiveIntegerField(default=1)),
                ('tags', models.CharField(blank=True, default='', max_length=255)),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='approved', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='skill_management.skillcategory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'skills',
                'ordering': ['-created_at'],
            },
        ),
    ]
