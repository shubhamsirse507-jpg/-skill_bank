from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(
                    choices=[
                        ('skill_request', 'Skill Swap Request'),
                        ('system', 'System Notification'),
                        ('message', 'Direct Message'),
                        ('achievement', 'Skill Achievement'),
                    ],
                    default='system',
                    max_length=30
                )),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('action_url', models.CharField(blank=True, default='', max_length=255)),
                ('action_text', models.CharField(blank=True, default='', max_length=100)),
                ('sender_name', models.CharField(blank=True, default='', max_length=100)),
                ('sender_avatar', models.CharField(blank=True, default='', max_length=255)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to='auth.user'
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
