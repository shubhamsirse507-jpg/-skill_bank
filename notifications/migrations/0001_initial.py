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
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('type', models.CharField(choices=[('exchange_request', 'Exchange Request'), ('exchange_accepted', 'Exchange Accepted'), ('booking_scheduled', 'Booking Scheduled'), ('review_received', 'Review Received'), ('system_notice', 'System Notice')], default='system_notice', max_length=30)),
                ('is_read', models.BooleanField(default=False)),
                ('action_url', models.CharField(blank=True, default='', max_length=255)),
                ('action_text', models.CharField(blank=True, default='', max_length=100)),
                ('sender_name', models.CharField(blank=True, default='', max_length=100)),
                ('sender_avatar', models.CharField(blank=True, default='', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
    ]
