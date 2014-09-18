
# uncomment and complete the following to set up your server name
#
#SERVERNAME = ""

#
# uncomment and complete the following to set up who should get cron reports
#
#CRON_EMAIL = ""

#
# These are overrides to defaults set in settings.py. To keep defaults, leave
# these values empty. To replace the defaults, uncomment the line and enter
# your changes here rather than making the changes in settings.py.
#
DEBUG = True
# TEMPLATE_DEBUG = ""
# ADMINS = (('admin name', 'admin@admin.test'),)
# MANAGERS = ""
# HTTP_PORT = ""
# HTTPD_MEDIA = ""
# EMAIL_HOST = ""
# EMAIL_FROM = ""
# EMAIL_BCC = ""

# EMAIL_BACKEND = ""
# EMAIL_FILE_PATH = ""

# PERSONA_EMAIL = ""
# PERSONA_PASSWORD = ""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'assessments_service', # Or path to database file if using sqlite3.
#         'USER': 'assessments_user', # Not used with sqlite3.
#         'PASSWORD': 'weLoveOurAssessments!', # Not used with sqlite3.
#         'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '', # Set to empty string for default. Not used with sqlite3.
#         'OPTIONS': {
#             "init_command": "SET foreign_key_checks=0;",
#         }# mysql only, to prevent relations to non-existent rows from killing db...
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

if True:
    import dj_database_url
    DATABASES['default'] = dj_database_url.config() or DATABASES['default']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
ALLOWED_HOSTS = ['assessments-dev.mit.edu']
STATIC_URL = '/static/'

STATICFILES_DIRS = ( '/Users/anna/Documents/ims_lti_py_django/static', )
CONSUMER_KEY = "__consumer_key__"
LTI_SECRET = "__lti_secret__"


URL_ASSESSMENTS = "https://assessments-dev.mit.edu/api/v1"
PUBLIC_KEY='E5IFLfKuxNdhLKh+tLRN'
PRIVATE_KEY='0/e10IAyBE1VkqtK+8PzPh2ViXVl5us1Zrj2rYQs'
ASSESSMENTS_HOST='assessments-dev.mit.edu'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
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
        },
        'custom': {
        	'level': 'INFO',
        	'class': 'logging.handlers.RotatingFileHandler',
        	'filename': '/Users/cjshaw/Documents/Projects/AssessmentService/assessments/logs/assessments.log',
        	'mode': 'a',
        	'maxBytes': 10000000,
        	'backupCount': 5,
        	'formatter': 'verbose'
        }
    },
    'loggers': {
    	'': {
    		'handlers': ['custom'],
    		'level': 'INFO',
    		'propagate': True,
    	},
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# /Users/cjshaw/Documents/Projects/RELATE/edx_resource_bank-master/media/
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
# STATIC_URL = '/static/'

# The Chrome Webdriver for Selenium testing
SELENIUM_WEBDRIVER = ''

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
# ALLOWED_HOSTS = ['127.0.0.1']

SECURE_PATH = 'www.mit.edu'

LOGIN_URL = '/'

# Additional locations of static files
# STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # '/Users/cjshaw/Documents/Projects/AssessmentService/assessments/users/static',
# )

# MC3_HOST = 'oki-dev.mit.edu'
#
# # certificate location for talking to IS&T Membership Service
# CERT = '/Users/cjshaw/Documents/Projects/AssessmentService/assessments/users/pqq.cer'
# KEY = '/Users/cjshaw/Documents/Projects/PQQ/pqq-key.pem'
# MEMBERSHIP = 'https://learning-modules-test.mit.edu:8443/service/membership/'
#
# # ASSESSMENTS = 'assessments-dev.mit.edu'
# # ASSESSMENTS_SERVICE = 'https://' + ASSESSMENTS + '/api/v1/assessment/'
# ASSESSMENTS = '127.0.0.1:8000'
# ASSESSMENTS_SERVICE = 'http://' + ASSESSMENTS + '/api/v1/assessment/'
# APP_PUBLIC = 'E5IFLfKuxNdhLKh+tLRN'
# APP_PRIVATE = '0/e10IAyBE1VkqtK+8PzPh2ViXVl5us1Zrj2rYQs'
#
# # LTI consumer key and secret
# LTI_KEY = 'foo'
# LTI_SECRET = 'O7qlLjzmBpicuu8HKNJnGTf2edF41WUA174L1uIW'