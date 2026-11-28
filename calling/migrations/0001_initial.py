import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleCallPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(choices=[('user', 'User / Learner'), ('teacher', 'Teacher / Mentor'), ('admin', 'Admin')], max_length=30, unique=True)),
                ('can_call', models.BooleanField(default=True)),
                ('can_host', models.BooleanField(default=True)),
                ('can_screen_share', models.BooleanField(default=True)),
                ('can_create_group_call', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Role Call Permission',
                'verbose_name_plural': 'Role Call Permissions',
                'db_table': 'calling_role_permissions',
                'ordering': ['role_name'],
            },
        ),
        migrations.CreateModel(
            name='PlatformCallSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calling_enabled', models.BooleanField(default=True, help_text='Global master switch to enable or disable calling across the platform.')),
                ('max_participants', models.PositiveSmallIntegerField(default=10, help_text='Maximum participants allowed in any call room (server-capped at 10).', validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(10)])),
                ('max_call_duration_minutes', models.PositiveIntegerField(default=60, help_text='Maximum duration in minutes before a call ends automatically.', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(480)])),
                ('allow_audio_calls', models.BooleanField(default=True)),
                ('allow_video_calls', models.BooleanField(default=True)),
                ('allow_screen_share', models.BooleanField(default=True)),
                ('allow_in_call_chat', models.BooleanField(default=True)),
                ('allow_waiting_room', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_call_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Platform Call Settings',
                'verbose_name_plural': 'Platform Call Settings',
                'db_table': 'calling_platform_settings',
            },
        ),
        migrations.CreateModel(
            name='CallRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_code', models.CharField(db_index=True, max_length=64, unique=True)),
                ('title', models.CharField(default='Skill-Verse Call', max_length=200)),
                ('call_kind', models.CharField(choices=[('one_to_one', 'One-to-One'), ('group', 'Group Call'), ('batch', 'Batch Class'), ('doubt', 'Doubt Session')], default='one_to_one', max_length=20)),
                ('media_type', models.CharField(choices=[('audio', 'Audio Only'), ('video', 'Audio & Video')], default='video', max_length=10)),
                ('max_participants', models.PositiveSmallIntegerField(default=10, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(10)])),
                ('is_locked', models.BooleanField(default=False)),
                ('waiting_room_enabled', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('ended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ended_call_rooms', to=settings.AUTH_USER_MODEL)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_call_rooms', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Call Room',
                'verbose_name_plural': 'Call Rooms',
                'db_table': 'calling_rooms',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='CallLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_type', models.CharField(choices=[('audio', 'Audio Call'), ('video', 'Video Call'), ('group', 'Group Call')], default='video', max_length=12)),
                ('status', models.CharField(choices=[('ringing', 'Ringing'), ('active', 'Active'), ('completed', 'Completed'), ('missed', 'Missed'), ('declined', 'Declined'), ('busy', 'Busy'), ('cancelled', 'Cancelled'), ('ended_by_admin', 'Ended by Admin')], db_index=True, default='ringing', max_length=20)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('answered_at', models.DateTimeField(blank=True, null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('duration_seconds', models.PositiveIntegerField(default=0)),
                ('notes', models.CharField(blank=True, default='', max_length=255)),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_call_logs', to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incoming_call_logs', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to='calling.callroom')),
            ],
            options={
                'verbose_name': 'Call Log',
                'verbose_name_plural': 'Call Logs',
                'db_table': 'calling_logs',
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='CallAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=200)),
                ('target_room_code', models.CharField(blank=True, default='', max_length=64)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='call_audit_logs', to=settings.AUTH_USER_MODEL)),
                ('target_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='targeted_call_audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Call Audit Log',
                'verbose_name_plural': 'Call Audit Logs',
                'db_table': 'calling_audit_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserCallPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_blocked_from_calling', models.BooleanField(default=False, help_text='If True, this user cannot initiate, receive, or join calls.')),
                ('block_reason', models.CharField(blank=True, default='', max_length=255)),
                ('can_call', models.BooleanField(blank=True, null=True)),
                ('can_host', models.BooleanField(blank=True, null=True)),
                ('can_screen_share', models.BooleanField(blank=True, null=True)),
                ('can_create_group_call', models.BooleanField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='call_permissions_modified', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='call_permission', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Call Permission',
                'verbose_name_plural': 'User Call Permissions',
                'db_table': 'calling_user_permissions',
            },
        ),
    ]
