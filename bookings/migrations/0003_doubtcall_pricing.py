from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_batch_doubtcall_batchenrollment'),
    ]

    operations = [
        migrations.AddField(
            model_name='doubtcall',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('50.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='admin_fee',
            field=models.DecimalField(decimal_places=2, default=Decimal('5.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='teacher_earning',
            field=models.DecimalField(decimal_places=2, default=Decimal('45.00'), max_digits=10),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='duration_minutes',
            field=models.IntegerField(default=15),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='started_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='ended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='doubtcall',
            name='is_teacher_paid',
            field=models.BooleanField(default=False),
        ),
    ]
