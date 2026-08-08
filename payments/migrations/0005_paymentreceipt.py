import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_wallet_wallettransaction'),
        ('bookings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt_number', models.CharField(default=uuid.uuid4, max_length=50, unique=True)),
                ('transaction_id', models.CharField(blank=True, max_length=80, null=True, unique=True)),
                ('item_title', models.CharField(max_length=200)),
                ('category_name', models.CharField(blank=True, default='General', max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(default='SkillBank Wallet', max_length=50)),
                ('status', models.CharField(choices=[('PAID', 'Paid / Completed'), ('REFUNDED', 'Refunded'), ('FAILED', 'Failed')], default='PAID', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receipts', to='bookings.batch')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_receipts', to=settings.AUTH_USER_MODEL)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_receipts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'payment_receipts',
                'ordering': ['-created_at'],
            },
        ),
    ]
