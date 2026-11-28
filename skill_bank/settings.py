"""
Django settings for Skill Exchange Platform (single, canonical project).
Reads all sensitive values from .env via python-dotenv.
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# SQLite is used — no extra driver needed (built into Python)

# Load .env
load_dotenv()

# ---------------------------------------------------------------------------
# Base Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-replace-this-in-production-NOW'
)
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://skill-verse-platform.onrender.com',
    'https://skill-bank-platform.onrender.com',
    'https://*.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# ---------------------------------------------------------------------------
# Application Definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',

    # Platform apps (canonical project — single settings.py)
    'authentication',       # Login / Register / OTP / Password Reset
    'profiles',             # UserProfile model + CRUD
    'skill_management',     # Canonical Skill + SkillCategory
    'messaging',            # SkillExchange + Conversation + Message
    'bookings',             # Booking model
    'ratings',              # ReviewRating
    'notifications',        # Notification
    'admin_panel',          # PlatformReport, PlatformNotice, AuditLog
    'search',               # Search/filter service
    'chatboat',             # AI chat assistant
    'dashboard',            # Landing dashboard (legacy, kept)
    'user_dashboard',       # User-facing dashboard views
    'payments',             # Skill-Verse Wallet & Payments
    'calling',              # Self-hosted WebRTC calling settings, logs & admin controls
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'skill_bank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Inject unread badge counts into every template
                'notifications.context_processors.unread_counts',
            ],
        },
    },
]

WSGI_APPLICATION = 'skill_bank.wsgi.application'

# ---------------------------------------------------------------------------
# Database Configuration (SQLite local, PostgreSQL / DATABASE_URL in Prod)
# ---------------------------------------------------------------------------
try:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=f"sqlite:///{BASE_DIR / os.environ.get('DB_NAME', 'db.sqlite3')}",
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
except ImportError:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.environ.get('DB_NAME', 'db.sqlite3'),
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Password Validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / os.environ.get('STATIC_ROOT', 'staticfiles')

# Collect static files from all app-level static directories
_candidate_static_dirs = [
    BASE_DIR / 'static',
    BASE_DIR / 'user_dashboard' / 'static',
    BASE_DIR / 'chatboat' / 'static',
    BASE_DIR / 'skill_bank' / 'admin_panel' / 'static',
    BASE_DIR / 'skill_bank' / 'messaging' / 'static',
    BASE_DIR / 'skill_bank' / 'ratings' / 'static',
]
STATICFILES_DIRS = [d for d in _candidate_static_dirs if d.exists()]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# STATICFILES_STORAGE is deprecated in Django 4.2+ — use STORAGES dict above instead.
# Do NOT re-declare it here; it conflicts with the STORAGES dict and causes warnings.
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / os.environ.get('MEDIA_ROOT', 'media')

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'skill_bank.utils.custom_exception_handler',
}

# ---------------------------------------------------------------------------
# JWT Settings
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.environ.get('ACCESS_TOKEN_LIFETIME_MINUTES', 60))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.environ.get('REFRESH_TOKEN_LIFETIME_DAYS', 7))
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG  # open in dev, restricted in prod
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '').strip()
_raw_email_pass = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_PASSWORD = _raw_email_pass.replace(' ', '').strip()
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    f"Skill-Verse <{EMAIL_HOST_USER}>" if EMAIL_HOST_USER else 'noreply@Skill-Verse.com'
)
_default_email_backend = (
    'django.core.mail.backends.smtp.EmailBackend'
    if (EMAIL_HOST_PASSWORD and EMAIL_HOST_USER)
    else 'django.core.mail.backends.console.EmailBackend'
)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', _default_email_backend)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
_env_use_tls = os.environ.get('EMAIL_USE_TLS', '').strip().lower()
_env_use_ssl = os.environ.get('EMAIL_USE_SSL', '').strip().lower()
if EMAIL_PORT == 465 and _env_use_tls != 'true':
    EMAIL_USE_SSL = True if _env_use_ssl != 'false' else False
    EMAIL_USE_TLS = False
else:
    EMAIL_USE_TLS = True if _env_use_tls != 'false' else False
    EMAIL_USE_SSL = False
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 15))  # 15s prevents cloud handshake timeouts
OTP_DEV_LOG = os.environ.get('OTP_DEV_LOG', 'False').lower() == 'true'

# Brevo (Sendinblue) HTTPS Transactional Email API (bypasses cloud SMTP port blocks)
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '').strip()
BREVO_SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL', EMAIL_HOST_USER or '').strip()
BREVO_SENDER_NAME = os.environ.get('BREVO_SENDER_NAME', 'Skill-Verse').strip()

# ---------------------------------------------------------------------------
# Security & Cloud Proxy Configuration
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

if not DEBUG:
    # Render.com terminates SSL at its load balancer — DO NOT redirect internally.
    # SECURE_PROXY_SSL_HEADER above handles detection of HTTPS correctly.
    SECURE_SSL_REDIRECT = False  # Never True on Render (causes infinite redirect loops)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# ---------------------------------------------------------------------------
# Logging — structured, no bare print() in production
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',  # Raised from WARNING so 500 errors appear in Render logs
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'authentication': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'messaging': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'ratings': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'admin_panel': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'profiles': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'bookings': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'skill_management': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}

# ---------------------------------------------------------------------------
# Self-Hosted WebRTC Calling Integration (Node + Socket.IO + mediasoup)
# ---------------------------------------------------------------------------
WEBRTC_SERVER_URL = os.environ.get('WEBRTC_SERVER_URL', 'http://localhost:4000').rstrip('/')
INTERNAL_CALLING_SECRET = os.environ.get(
    'INTERNAL_CALLING_SECRET',
    'skillverse-internal-bridge-secret-dev',
)

# ---------------------------------------------------------------------------
# Swagger / OpenAPI
# ---------------------------------------------------------------------------
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

# ---------------------------------------------------------------------------
# Teacher Qualification Exam & Browser Proctoring (Privacy-first)
# ---------------------------------------------------------------------------
PRIVATE_MEDIA_ROOT = BASE_DIR / 'private_media'
PROCTOR_SNAPSHOTS_ENABLED = os.environ.get('PROCTOR_SNAPSHOTS_ENABLED', 'False').lower() == 'true'
PROCTOR_RETENTION_DAYS = int(os.environ.get('PROCTOR_RETENTION_DAYS', 14))
PROCTOR_ALLOW_NO_CAMERA = os.environ.get('PROCTOR_ALLOW_NO_CAMERA', 'False').lower() == 'true'
PROCTOR_AUTO_SUBMIT_THRESHOLD = int(os.environ.get('PROCTOR_AUTO_SUBMIT_THRESHOLD', 0))
PROCTOR_PRIVACY_NOTE = (
    "Camera proctoring runs entirely inside your browser. Video is never uploaded. "
    "Only timestamped monitoring events are recorded"
    + (" along with small still snapshots on flagged events" if PROCTOR_SNAPSHOTS_ENABLED else "")
    + f" and retained for {PROCTOR_RETENTION_DAYS} days."
)
