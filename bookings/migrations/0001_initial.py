import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('meeting_mode', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline / In-Person')], default='online', max_length=10)),
                ('meeting_link', models.URLField(blank=True, default='')),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('request', models.ForeignKey(help_text='The accepted skill exchange this booking belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='messaging.skillexchange')),
            ],
            options={
                'db_table': 'bookings',
                'ordering': ['-scheduled_date', '-start_time'],
            },
        ),
    ]
