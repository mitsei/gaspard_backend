"""
Django settings for ims_lti_py_django project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))



FN_CREDENTIALS = "settings_credentials.py"


def msg_credentials():
    msg = "*** Please edit the %s file with the required settings for authentication. ***" %(FN_CREDENTIALS, )
    stars = "*" * len(msg)
    return "\n\n%s\n%s\n%s\n\n" %(stars, msg, stars)

try:
    import settings_credentials

except ImportError:
    from os.path import dirname, abspath
    import shutil
    thisdir = dirname(abspath(__file__))
    shutil.copy2("%s/%s.skel" % (thisdir, FN_CREDENTIALS), "%s/%s" % (thisdir, FN_CREDENTIALS))
    print msg_credentials()
    exit(1)


DATABASES = settings_credentials.DATABASES
ALLOWED_HOSTS = settings_credentials.__dict__.get('ALLOWED_HOSTS')
STATICFILES_DIRS = settings_credentials.__dict__.get('STATICFILES_DIRS')
STATIC_ROOT=settings_credentials.__dict__.get('STATIC_ROOT')
STATIC_URL = settings_credentials.__dict__.get('STATIC_URL')
CONSUMER_KEY = settings_credentials.__dict__.get('CONSUMER_KEY')
LTI_SECRET = settings_credentials.__dict__.get('LTI_SECRET')
URL_ASSESSMENTS = settings_credentials.__dict__.get('URL_ASSESSMENTS')
PUBLIC_KEY = settings_credentials.__dict__.get('PUBLIC_KEY')
PRIVATE_KEY = settings_credentials.__dict__.get('PRIVATE_KEY')
ASSESSMENTS_HOST = settings_credentials.__dict__.get('ASSESSMENTS_HOST')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^-nmp6((#y35$613xtxr!#dm9kedo2#2=+xvj)7nf-0670f^pp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
## IMS LTI
    'ims_lti_py_sample'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ims_lti_py_django.urls'

WSGI_APPLICATION = 'ims_lti_py_django.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
#
#
#
# if True:
#     import dj_database_url
#     DATABASES['default'] = dj_database_url.config() or DATABASES['default']

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



## LTI Parameters
X_FRAME_OPTIONS = 'ALLOW-FROM: *'
LTI_DEBUG = True

LTI_URL_FIX = {
    "https://localhost/":"http://192.168.33.10/"
}
## Heroku SSL proxy fix
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


