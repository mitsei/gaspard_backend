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


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^-nmp6((#y35$613xtxr!#dm9kedo2#2=+xvj)7nf-0670f^pp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['assessments-dev.mit.edu']


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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

if True:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config() or DATABASES['default']

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT='/Users/anna/Documents/ims_lti_py_django'
STATICFILES_DIRS = ( '/Users/anna/Documents/ims_lti_py_django/static', )
## LTI Parameters
X_FRAME_OPTIONS = 'ALLOW-FROM: *'
LTI_DEBUG = True
CONSUMER_KEY = "__consumer_key__"
LTI_SECRET = "__lti_secret__"
LTI_URL_FIX = {
    "https://localhost/":"http://192.168.33.10/"
}
## Heroku SSL proxy fix
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


URL_ASSESSMENTS = "https://assessments-dev.mit.edu/api/v1"
PUBLIC_KEY='E5IFLfKuxNdhLKh+tLRN'
PRIVATE_KEY='0/e10IAyBE1VkqtK+8PzPh2ViXVl5us1Zrj2rYQs'
ASSESSMENTS_HOST='assessments-dev.mit.edu'