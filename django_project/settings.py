"""
Django settings para Rey Pipas — optimizado para Replit
Sistema de Gestión de Distribución de Agua
"""

import os
from pathlib import Path
from django.contrib.messages import constants as messages

# --- Rutas base -------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad --------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-rey-pipas-dev-key-2025")
DEBUG      = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.getenv('REPL_SLUG')}.{os.getenv('REPL_OWNER')}.repl.co"
]



# --- Dominios extra de Replit ------------------------------------------
REPLIT_DEV_DOMAIN  = os.getenv("REPLIT_DEV_DOMAIN")       # ej. 5465ca6d-…kirk.replit.dev
REPLIT_DOMAINS_ENV = os.getenv("REPLIT_DOMAINS", "")      # lista separada por comas

# 1) ALLOWED_HOSTS
ALLOWED_HOSTS += ["*.repl.co", "*.replit.dev"]            # comodines
if REPLIT_DEV_DOMAIN:
    ALLOWED_HOSTS.append(REPLIT_DEV_DOMAIN)
if REPLIT_DOMAINS_ENV:
    ALLOWED_HOSTS += REPLIT_DOMAINS_ENV.split(",")

# 2) CSRF_TRUSTED_ORIGINS (esquema https:// obligatorio)
CSRF_TRUSTED_ORIGINS += [
    "https://*.repl.co",
    "https://*.replit.dev",
]
if REPLIT_DEV_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{REPLIT_DEV_DOMAIN}")
for d in REPLIT_DOMAINS_ENV.split(","):
    if d:
        CSRF_TRUSTED_ORIGINS.append(f"https://{d}")




# --- Apps -------------------------------------------------------------------
INSTALLED_APPS = [
    # Django default
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Proyecto
    "apps.users",
    "apps.orders",
    "apps.vehicles",
    "apps.payments",
    "apps.core",
    "apps.messages",        # ← con el prefijo apps.


     "widget_tweaks",
]

# --- Middleware -------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← nuevo
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URLs / WSGI ------------------------------------------------------------
ROOT_URLCONF = "django_project.urls"
WSGI_APPLICATION = "django_project.wsgi.application"


# --- Templates --------------------------------------------------------------
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

# --- Base de datos ----------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Passwords --------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalización ---------------------------------------------------
LANGUAGE_CODE = "es-mx"
TIME_ZONE     = "America/Mexico_City"
USE_I18N = True
USE_TZ   = True

# --- Archivos estáticos / media --------------------------------------------
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"       # Pasta final de collectstatic
# Archivos estáticos globales (carpeta static/ a nivel manage.py)
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"

# --- Modelo de usuario personalizado ---------------------------------------
AUTH_USER_MODEL = "users.User"

# --- Login / logout ---------------------------------------------------------
LOGIN_URL          = "/auth/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# --- Mensajes ---------------------------------------------------------------
MESSAGE_TAGS = {
    messages.DEBUG:   "debug",
    messages.INFO:    "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR:   "error",
}

# --- Default prim. key type -------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
