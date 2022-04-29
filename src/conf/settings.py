import logging
import os

from envparse import env
from schema import Or

env.read_envfile()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', cast=bool, default=True)

ALLOWED_HOSTS = ['*']

log_level_names = [
    logging.getLevelName(level)
    for level in (logging.CRITICAL,
                  logging.ERROR,
                  logging.WARNING,
                  logging.INFO,
                  logging.DEBUG,
                  logging.NOTSET)
]

error_log_level = logging.getLevelName(logging.ERROR)


def get_log_level_from_env(var_name, default):
    validator = Or(*log_level_names,
                   error=f'{var_name} failed. "{{}}" not in {log_level_names}')
    return validator.validate(env(var_name, default))


LOG_LEVEL = get_log_level_from_env('LOG_LEVEL', error_log_level)

SENTRY_DSN = env('SENTRY_DSN', None)

ENVIRONMENT = env('ENVIRONMENT', '') or 'local'

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        integrations=[DjangoIntegration()],
    )

LOGGING_FORMATTER = env('LOGGING_FORMATTER', default='json')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'json': {
            '()': 'smart_json_log_formatter.JsonFormatter',
        },
        'simple': {
            'format': '\t'.join((
                '%(asctime)s',
                '%(levelname)s',
                '%(pathname)s:%(lineno)s',
                '%(message)s',
            )),
        },
    },
    'handlers': {
        'stdout': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': LOGGING_FORMATTER,
            'stream': 'ext://sys.stdout',
        }
    },
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['stdout'],
    },
    'loggers': {
        'wsgi': {
            # это замена для django.request
            'handlers': ['stdout'],
            'level': LOG_LEVEL,
        },
        'main': {
            'level': LOG_LEVEL,
            'handlers': ['stdout'],
            'propagate': False,
        },
        'requests': {
            'level': LOG_LEVEL,
            'handlers': ['stdout'],
            'propagate': False,
        },
        'celery.app.trace': {
            'level': LOG_LEVEL,
            'handlers': ['stdout'],
            'propagate': False
        },

    },
}

# Application definition

PREREQ_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'health_check',  # required
    'health_check.db',
    'request_id',
    'django_celery_beat',
    'django_metrics',
    'cloudinary',
    'mptt',
]

PROJECT_APPS = [
    'apps.user',
    'apps.support',
    'apps.bot_user',
]

INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS
MIDDLEWARE = [
    'django_metrics.middleware.CommonMetricMiddleware',
    'request_id.middleware.RequestIdMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middlewares.request_middlewares.JsonParamsToRequest',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

PGBOUNCER_HOST = env('PGBOUNCER_HOST', default='')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB_NAME', default=''),
        'USER': env('POSTGRES_DB_USER', default=''),
        'PASSWORD': env('POSTGRES_DB_PASSWORD', default=''),
        'HOST': PGBOUNCER_HOST or env('POSTGRES_DB_HOST', default=''),
        'PORT': env('POSTGRES_DB_PORT', default=''),
        # если подключение через pgBouncer в режиме transaction pooling, серверные курсоры нужно отключить
        # https://docs.djangoproject.com/en/2.2/ref/databases/#transaction-pooling-server-side-cursors
        'DISABLE_SERVER_SIDE_CURSORS': bool(PGBOUNCER_HOST)
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Пути к админке и статике для соответствия схеме именования доменных имен
ADMIN_PATH = env('DJANGO_ADMIN_PATH', '')
STATIC_URL = os.path.join('/', ADMIN_PATH, 'static/')
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(BASE_DIR, 'static'))

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

CONN_MAX_AGE = 100

API_VERSION = env('API_VERSION', default='DEV')
# Cache config
REDIS_URL = env('REDIS_URL', default='')
CACHES = {
    'default':
        {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient"
            },
        }
}

SERVICE_NAME = env('SERVICE_NAME', default='')
ADMIN_PREFIX_URL = env('ADMIN_PREFIX_URL', default='')
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_TASK_SERIALIZER = 'ujson'
CELERY_RESULT_SERIALIZER = 'ujson'
CELERY_BROKER_URL = REDIS_URL
CELERY_BROKER_CONNECTION_MAX_RETRIES = 2
CELERY_QUEUE_MAX_RETRIES = 3
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'max_retries': 3,
}

# THIS IS EXAMPLE FOR SERVICE
SENTRY_URL_FOR_EXAMPLE = ""
SENTRY_API_TOKEN = ""

TG_TOKEN_SUPPORT_BOT = env('TG_TOKEN_SUPPORT_BOT', None)
TG_SUPPORT_BOT_ID = env('TG_SUPPORT_BOT_ID', None)
TG_TOKEN_MIM_BOT = env('TG_TOKEN_MIM_BOT', None)
TG_WAREHOUSE_CHAT = env('TG_WAREHOUSE_CHAT', None)

OMNIORDER_DOMAIN = env('OMNIORDER_DOMAIN', None)
PYRAMID_DOMAIN = env('PYRAMID_DOMAIN', None)
PYRAMID_PAGE_LIMIT = 10

AUTH_API_ENDPOINT = env('AUTH_API_ENDPOINT', None)
AUTH_API_REFERRER = env('AUTH_API_REFERRER', None)

BLINGER_WEBHOOK_URL = env('BLINGER_WEBHOOK_URL', None)
BLINGER_TOKEN = env('BLINGER_TOKEN', None)
BLINGER_USER_ID = env('BLINGER_CHANNEL_ID', None)
BLINGER_CHANNEL_ID = env('BLINGER_CHANNEL_ID', None)

JIRA_URL = env('JIRA_URL', default='')
JIRA_EMAIL = env('JIRA_EMAIL', default='')
JIRA_PASSWORD = env('JIRA_PASSWORD', default='')
JIRA_TOKEN = env('JIRA_TOKEN', default='')
JIRA_PROJECT_KEY = env('JIRA_PROJECT_KEY', default='INCOL')

CLOUDINARY = {
    'cloud_name': env('CLOUDINARY_NAME', None),
    'api_key': env('CLOUDINARY_API_KEY', None),
    'api_secret': env('CLOUDINARY_SECRET', None),
}
