"""
Main WAVES application settings files
"""
from __future__ import unicode_literals
import environ
import sys
from os.path import dirname, join, exists

BASE_DIR = dirname(dirname(dirname(__file__)))
STATIC_URL = '/static/'
MEDIA_ROOT = join(BASE_DIR, 'media')
MEDIA_URL = "/media/"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'profiles', 'templates'),
            join(BASE_DIR, 'accounts', 'templates'),
            join(BASE_DIR, 'waves', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'waves.utils.context_theme_processor.css_theme',
            ],
        },
    },
]

# Django main environment file (issued from local.env)
env = environ.Env()
environ.Env.read_env(join(dirname(__file__), 'local.env'))
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')
WAVES_ENV_FILE = env.str('WAVES_ENV_FILE', None)
# DATABASE configuration
DATABASES = {
    'default': env.db(default='sqlite:///' + dirname(BASE_DIR) + '/waves.sample.sqlite3'),
}
# patch to use in memory database for testing
if 'test' in sys.argv:
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

REGISTRATION_SALT = env.str('REGISTRATION_SALT')
# LOG FILE ROOT
LOG_ROOT = dirname(BASE_DIR) + '/logs'
STATIC_ROOT = join(dirname(BASE_DIR), 'staticfiles')
# Application definition
INSTALLED_APPS = (
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'authtools',
    'adminsortable2',
    'jet',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # WAVES required dependencies
    'waves',
    'profiles',
    'accounts',
    'mptt',
    'django_countries',
    'crispy_forms',
    'easy_thumbnails',
    'mail_templated',
    'rest_framework',
    'rest_framework_docs',
    # 'corsheaders',
    'ckeditor',
    'bootstrap_themes',
)
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
ROOT_URLCONF = 'waves_services.urls'
WSGI_APPLICATION = 'waves_services.wsgi.application'
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True
# Authentication Settings
AUTH_USER_MODEL = 'authtools.User'
# Thumbnails configuration
THUMBNAIL_EXTENSION = 'png'  # Or any extn for your thumbnails
# DRF Configuration
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'profiles.auth.APIKeyAuthBackend',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework_xml.parsers.XMLParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
# FILE_UPLOAD_MAX_MEMORY_SIZE = 0FILE_UPLOAD_DIRECTORY_PERMISSIONS
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755
FILE_UPLOAD_PERMISSIONS = 0o775
# Default Site id
SITE_ID = 1
# Tabbed Admin configuration
TABBED_ADMIN_USE_JQUERY_UI = False
THUMBNAIL_EXTENSION = 'png'
# DJANGO crontab settings
CRONTAB_LOCK_JOBS = True
CRONTAB_DJANGO_SETTINGS_MODULE = 'waves_services.settings.cron'
CRONJOBS = [('1 0 * * *', 'waves.managers.cron.purge_old_jobs')]
# Django countries first items
COUNTRIES_FIRST = ['FR', 'GB', 'US', 'DE']
JET_SIDE_MENU_COMPACT = True
# MAILS
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
JET_THEMES = [
    {
        'theme': 'default', # theme folder name
        'color': '#47bac1', # color of the theme's button in user menu
        'title': 'Default' # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]
CKEDITOR_CONFIGS = {
    'default': {
        'height': 150,
    },
}
