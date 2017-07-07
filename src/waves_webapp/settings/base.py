"""
Main WAVES application settings files
"""
from __future__ import unicode_literals

from os.path import dirname, join


LOGGING_CONFIG = None
BASE_DIR = dirname(dirname(dirname(dirname(__file__))))
STATIC_URL = '/static/'
MEDIA_ROOT = join(dirname(BASE_DIR), 'media')
MEDIA_URL = "/media/"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
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
                'constance.context_processors.config',
            ],
        },
    },
]

# LOG FILE ROOC
LOG_ROOT = BASE_DIR + '/logs'
STATIC_ROOT = join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    join(BASE_DIR, 'src', 'waves_demo', 'static'),
]

# Application definition
INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'jet',
    'jet.dashboard',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'waves',
    'waves_demo',
    # WAVES required dependencies
    'authtools',
    'adminsortable2',
    'accounts',
    'bootstrap_themes',
    'ckeditor',
    'django_countries',
    'crispy_forms',
    'easy_thumbnails',
    'mail_templated',
    'profiles',
    'rest_framework',
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
ROOT_URLCONF = 'waves_webapp.urls'
WSGI_APPLICATION = 'waves_webapp.wsgi.application'
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
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'profiles.auth.APIKeyAuthBackend',
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
# Django countries first items
COUNTRIES_FIRST = ['FR', 'GB', 'US', 'DE']
JET_SIDE_MENU_COMPACT = True
# MAILS
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
JET_THEMES = [
    {
        'theme': 'default',  # theme folder name
        'color': '#47bac1',  # color of the theme's button in user menu
        'title': 'Default'  # theme title
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
# TODO in order to enable sibling, either overwrite to set-it up per model, or add custom filter for submissions
# (keep current service)
JET_CHANGE_FORM_SIBLING_LINKS = False

CRISPY_TEMPLATE_PACK = 'bootstrap3'

ACCOUNT_ACTIVATION_DAYS = 7

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

WAVES_CORE = {
    'ACCOUNT_ACTIVATION_DAYS': 14,
    'ADMIN_EMAIL': 'admin_waves@atgc-montpellier.fr',
    'ALLOW_JOB_SUBMISSION': True,
    'APP_NAME': 'WAVES DEMO',
    'SERVICES_EMAIL': 'services@atgc-montpellier.fr',
    'ADAPTORS_CLASSES': (
        'waves.adaptors.core.shell.SshShellAdaptor',
        'waves.adaptors.core.cluster.LocalClusterAdaptor',
        'waves.adaptors.core.shell.SshKeyShellAdaptor',
        'waves.adaptors.core.shell.LocalShellAdaptor',
        'waves.adaptors.core.cluster.SshClusterAdaptor',
        'waves.adaptors.core.cluster.SshKeyClusterAdaptor',
    ),
    'SERVICE_MODEL': 'waves_demo.DemoWavesService'
}
