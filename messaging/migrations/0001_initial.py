import django.db.models.deletion
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('skill_management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SkillExchange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Topic or goal of the skill exchange', max_length=200)),
                ('message', models.TextField(blank=True, default='', help_text='Initial message from requester')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_exchanges', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_exchanges', to=settings.AUTH_USER_MODEL)),
                ('skill', models.ForeignKey(help_text='The skill being exchanged', on_delete=django.db.models.deletion.CASCADE, related_name='exchanges', to='skill_management.skill')),
            ],
            options={
                'db_table': 'exchange_requests',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='conversation', to='messaging.skillexchange')),
                ('user_one', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations_as_one', to=settings.AUTH_USER_MODEL)),
                ('user_two', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations_as_two', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'conversations',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_text', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('has_attachment', models.BooleanField(default=False)),
                ('attachment_name', models.CharField(blank=True, max_length=150, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='messaging.conversation')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'messages',
                'ordering': ['created_at'],
            },
        ),
    ]
