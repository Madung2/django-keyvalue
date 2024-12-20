"""
Django settings for DocTransformer project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""


from pathlib import Path
import environ
import os
# Initialise environment variables
env = environ.Env(
    DEBUG=(bool, True)  # default value for DEBUG
)

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
#environ.Env.read_env(env_file=BASE_DIR / '.env')
environ.Env.read_env(str(BASE_DIR/ '.env'))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
METATYPE = env.int('METATYPE',2)
NAS_BASE_PATH = env('NAS_BASE_PATH')
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = ['*']
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'TsExpert', # TsExpert앱
    'DocGenerator'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
################CORS########################
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'DocTransformer.urls'

CORS_ALLOWED_ORIGINS = [
    'http://121.162.129.61:30100',  # 프론트엔드 도메인
    'http://192.168.14.155:8501',
    'http://127.0.0.1:8000',
    'http://3.34.141.159:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8501',
    'http://localhost:8501',
    'http://shinhandemo.edentns.com:8000',
    'http://121.162.129.61:30080'
]
CORS_ORIGIN_WHITELIST = [
    'http://121.162.129.61:30100',  # 프론트엔드 도메인
    'http://192.168.14.155:8501',
    'http://127.0.0.1:8000',
    'http://3.34.141.159:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8501',
    'http://localhost:8501',
    'http://shinhandemo.edentns.com:8000',
    'http://121.162.129.61:30080'
]
CSRF_TRUSTED_ORIGINS = [
    'http://121.162.129.61:30100',  # 프론트엔드 도메인
    'http://192.168.14.155:8501',
    'http://127.0.0.1:8000',
    'http://3.34.141.159:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8501',
    'http://localhost:8501',
    'http://shinhandemo.edentns.com:8000',
    'http://121.162.129.61:30080'
]
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
SESSION_COOKIE_SECURE = False
################CORS########################
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'DocTransformer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


#### Celery Settings ########################################

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# 미디어 파일이 저장될 디렉토리 경로
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
