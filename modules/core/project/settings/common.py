# -*- coding: utf-8 -*-

import os, sys
ugettext = lambda s: s

ROOT_PATH = os.path.dirname(__file__)
SITE_ROOT = ROOT_PATH
PROJECT_ROOT = ROOT_PATH

sys.path.append(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT + '/apps/')
sys.path.append(PROJECT_ROOT + '/libs/')


SESSION_EXPIRE_AT_BROWSER_CLOSE = True

APPEND_SLASH = True

domain = ''

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(ROOT_PATH,'media')
MEDIA_URL = domain + '/media/'

LOGIN_REDIRECT_URL = '/'
STATIC_ROOT = os.path.join(ROOT_PATH,'static')
STATIC_URL = domain + '/static/'

STATICFILES_DIRS = (
    #!chuck_renders STATICFILES_DIRS
    os.path.join(ROOT_PATH, 'static'),
    #!end
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    #!chuck_renders STATICFILES_FINDERS
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #!end
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'uc#u_f*8wo*h(s6d!9klcw)fy)9#q#1-t5wcbr@6v5v5!cb-r2'

# List of callables that know how to import templates from various sources.

TEMPLATE_CONTEXT_PROCESSORS = (
    #!chuck_renders TEMPLATE_CONTEXT_PROCESSORS
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
    'django.core.context_processors.debug',
    #!end
)
TEMPLATE_LOADERS = (
    #!chuck_renders TEMPLATE_LOADERS
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #!end
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #!chuck_renders MIDDLEWARE_CLASSES
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #!end
    # Uncomment the next line for simple clickjacking protection:
     'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
#WSGI_APPLICATION = 'miniwave.wsgi.application'

TEMPLATE_DIRS = (
    #!chuck_renders TEMPLATE_DIRS
    os.path.join(ROOT_PATH,'templates'),
    #!end
)

INSTALLED_APPS = (
    #!chuck_renders INSTALLED_APPS
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    #!end
)

AUTHENTICATION_BACKENDS = ( 
    #!chuck_renders AUTHENTICATION_BACKENDS
    #'django.contrib.auth.backends.ModelBackend',
    #!end
    #'twitter_users.backends.TwitterBackend',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
#!chuck_renders SETTINGS
# Save timestamps in utc
USE_TZ = True

# cickhacking protection
X_FRAME_OPTIONS = 'DENY'
#!end
