from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_userprofile_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='two_factor_enabled',
            field=models.BooleanField(
                default=True,
                help_text='Enable Two-Factor Authentication (OTP via email) on login.'
            ),
        ),
    ]
