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
    "jazzmin",  # debe ir antes del admin
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
    "apps.unidades",

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

            # NUEVA línea para mensajes no leídos
            'apps.messages.context_processors.unread_messages_processor',
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



# ------------------------------------------------------------------
#   Desactivar WhiteNoise Manifest en DEBUG y durante los tests
# ------------------------------------------------------------------
if DEBUG or os.environ.get("PYTEST_CURRENT_TEST"):
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"



LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}


JAZZMIN_SETTINGS = {
    "site_title": "Rey Pipas",
    "site_header": "Rey Pipas Admin",
    "site_brand": "Rey Pipas",
    "welcome_sign": "Bienvenido al panel de administración",
    "copyright": "Rey Pipas",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "users.User": "fas fa-user-tie",
        "orders.Order": "fas fa-truck",
        "payments.Payment": "fas fa-money-bill-alt",
        "unidades.Unidad": "fas fa-tint",
    },
     "custom_css": "css/reypipas_admin.css",
}



JAZZMIN_UI_TWEAKS = {
    "theme": "default",  # sin modo oscuro
    "dark_mode_theme": None,
    "navbar": "navbar-white navbar-light",
    "accent": "accent-pink",
    "sidebar": "sidebar-light-pink",
    "brand_colour": "navbar-pink",
}
JAZZMIN_SETTINGS["site_logo"] = "img/logo-reypipas_f.png"


# --- CONFIGURACIONES PARA PERMITIR PWA EN IFRAME (FASE PILOTO) ---

# Permitir carga en iframe desde cualquier origen (incluye tu PWA en Replit)
X_FRAME_OPTIONS = 'ALLOWALL'

# Seguridad: Desactivamos bloqueos comunes para permitir embedding en pruebas
SECURE_FRAME_DENY = False
SECURE_CONTENT_TYPE_NOSNIFF = False

# CORS - Permitir llamadas entre dominios (de la PWA al backend Django)
INSTALLED_APPS += [
    'corsheaders',
]

MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Replit host temporalmente abierto
ALLOWED_HOSTS = ['*']

# OPCIONAL: si usas CSRF, permite al frontend desde otros orígenes


CSRF_TRUSTED_ORIGINS = [
    "https://5465ca6d-2ff9-4996-b6a9-deb05bd925a8-00-tk2w8rsj0cib.kirk.replit.dev"
]

