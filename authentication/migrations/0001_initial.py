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
            name='OTPVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_code', models.CharField(max_length=10)),
                ('purpose', models.CharField(choices=[('Registration', 'Registration'), ('Login', 'Login'), ('ForgotPassword', 'Forgot Password')], max_length=20)),
                ('expires_at', models.DateTimeField()),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otp_verifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'OTP Verification',
                'db_table': 'otp_verifications',
                'ordering': ['-created_at'],
            },
        ),
    ]
