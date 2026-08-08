from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='skillexchange',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Swap price (₹0 - ₹100 max)', max_digits=10),
        ),
    ]
