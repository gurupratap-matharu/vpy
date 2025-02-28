import os
from pathlib import Path

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = PROJECT_DIR.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = int(os.getenv("DEBUG", default=0))

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", default="").split(" ")

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", default="").split(" ")

INSTALLED_APPS = [
    "home",
    "search",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail_localize",
    "wagtail_localize.locales",
    "wagtail",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # Third party
    "django_extensions",
    "modelcluster",
    "taggit",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]

SITE_ID = 1

ROOT_URLCONF = "main.urls"

# Mailpit
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "127.0.0.1"
EMAIL_PORT = 1025

# Email
DEFAULT_FROM_EMAIL = "'Ventanita' <noreply@ventanita.com.py>"
DEFAULT_TO_EMAIL = "gurupratap.matharu@gmail.com"
SERVER_EMAIL = "wagtail@ventanita.com.py"
RECIPIENT_LIST = [
    "gurupratap.matharu@gmail.com",
    "veerplaying@gmail.com",
]

ADMINS = [
    ("Veer", "veerplaying@gmail.com"),
    ("Gurupratap", "gurupratap.matharu@gmail.com"),
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


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

LANGUAGE_CODE = "es"

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", _("English")),
    ("es", _("Spanish")),
    ("pt", _("Portuguese")),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "America/Asuncion"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

MESSAGE_TAGS = {messages.ERROR: "danger"}

# Default storage settings, with the staticfiles storage updated.
# See https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-STORAGES
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    # ManifestStaticFilesStorage is recommended in production, to prevent
    # outdated JavaScript / CSS assets being served from cache
    # (e.g. after a Wagtail upgrade).
    # See https://docs.djangoproject.com/en/5.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Django sets a maximum of 1000 fields per form by default, but particularly complex page models
# can exceed this limit within Wagtail's page editor.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000


# Wagtail settings

WAGTAIL_SITE_NAME = "Ventanita"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL")

# Allowed file extensions for documents in the document library.
# This can be omitted to allow all files, but note that this may present a security risk
# if untrusted users are allowed to upload files -
# see https://docs.wagtail.org/en/stable/advanced_topics/deploying.html#user-uploaded-files
WAGTAILDOCS_EXTENSIONS = [
    "csv",
    "docx",
    "key",
    "odt",
    "pdf",
    "pptx",
    "rtf",
    "txt",
    "xlsx",
    "zip",
]

# Pagination
DEFAULT_PER_PAGE = 8
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "warnings.log",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "WARNING",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
        "formatter": "verbose",
    },
    "loggers": {
        "wagtail": {
            "level": os.getenv("WAGTAIL_LOG_LEVEL", default="INFO"),
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "django": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["file", "mail_admins"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = None

if not DEBUG:
    EMAIL_HOST = "smtp.mailgun.org"
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 31536000

    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    X_FRAME_OPTIONS = "DENY"
