"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load our environmental variable
load_dotenv()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-syj96ft*=19sw6cfks$o)ba^(ob&tq48w=v)obi-7)k36pynx5"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.vercel.app', '.now.sh', '127.0.0.1',
                 'localhost', '53bc-2400-1a00-b060-1b87-a019-8bb1-92c4-e15b.ngrok-free.app']
CSRF_TRUSTED_ORIGINS = [
    'https://53bc-2400-1a00-b060-1b87-a019-8bb1-92c4-e15b.ngrok-free.app']
# Application definition

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "Home",
    "cart",
    "payment",
    'paypal.standard.ipn',
    'widget_tweaks',
    'markdownify',
    'administrator',
    'tinymce',


]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'administrator.middleware.SuperuserRequiredMiddleware',

]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart",
                "Home.context_processors.categories",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'railway',
#         'USER': 'postgres',
#         'PASSWORD': 'bucYIFhiWNohGoLaIjpIzvCbUriGRmhz',
#         'HOST': 'junction.proxy.rlwy.net',
#         'PORT': '14588',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/')]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# white noise static file stuff

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_build", "static")


DEFAULT_FILE_STORAGE = 'storages.backends.filesystem.FileSystemStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# add paypal settings
# set sandbox to true
PAYPAL_TEST = True

# business sandbox acc of paypal...
PAYPAL_RECEIVER_EMAIL = 'django-ecommerce@business.com'

# Enable stripping of disallowed tags
MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": ['a',
                           'abbr',
                           'acronym',
                           'b',
                           'blockquote',
                           'em',
                           'i',
                           'li',
                           'ol',
                           'p',
                           'strong',
                           'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', ]
    },

    "alternative": {
        "WHITELIST_TAGS": ['a',
                           'abbr',
                           'acronym',
                           'b',
                           'blockquote',
                           'em',
                           'i',
                           'li',
                           'ol',
                           'p',
                           'strong',
                           'ul'],
        "MARKDOWN_EXTENSIONS": ["markdown.extensions.fenced_code", ]
    }
}

TINYMCE_DEFAULT_CONFIG = {
    "height": 360,
    "width": 800,
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code fullscreen insertdatetime media table paste code help wordcount",
    "toolbar": "undo redo | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | code",
    "content_css": "default",
}
