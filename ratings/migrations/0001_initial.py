import django.db.models.deletion
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bookings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=5)),
                ('communication_rating', models.IntegerField(default=5)),
                ('clarity_rating', models.IntegerField(default=5)),
                ('punctuality_rating', models.IntegerField(default=5)),
                ('comment', models.TextField(blank=True, default='')),
                ('tags', models.CharField(blank=True, help_text='Comma separated highlights (e.g. Great Communicator, Patient)', max_length=255)),
                ('would_recommend', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='bookings.booking')),
                ('reviewed_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_received', to=settings.AUTH_USER_MODEL)),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_given', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'reviews',
                'ordering': ['-created_at'],
            },
        ),
    ]
