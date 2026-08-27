"""
Configuration du projet « Ciné-Catalogue » (Django 6.1).

Ce fichier est lu UNE fois au démarrage du serveur. Chaque bloc est commenté
pour que l'on sache à quoi il sert et pourquoi il est là.
"""

from datetime import timedelta
from pathlib import Path

# BASE_DIR = le dossier qui contient manage.py. Toutes les autres
# chemins du projet se construisent à partir de lui.
BASE_DIR = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------------
# Sécurité (valeurs de DÉVELOPPEMENT uniquement)
# ----------------------------------------------------------------------
# En production : la clé se met dans une variable d'environnement et DEBUG = False.
SECRET_KEY = "django-insecure-*qo^_7*h29(00_w!&!llb*z!7b3z92^ngd&0fg18m8#hw#eggz"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# ----------------------------------------------------------------------
# Applications installées
# ----------------------------------------------------------------------
INSTALLED_APPS = [
    # Applications fournies par Django
    "django.contrib.admin",          # l'interface /admin/
    "django.contrib.auth",           # utilisateurs, groupes, permissions
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",    # CSS / images
    # Bibliothèques tierces
    "rest_framework",                # Django REST Framework (l'API)
    "rest_framework_simplejwt",      # authentification par jetons JWT
    # Nos applications
    "films",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Fichier qui contient la table des URLs de départ.
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # DIRS = templates communs au projet. Ici on n'en a pas :
        # tous nos templates vivent dans films/templates/films/.
        "DIRS": [],
        # APP_DIRS = True : Django cherche automatiquement un dossier
        # `templates/` dans chaque application installée.
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ----------------------------------------------------------------------
# Base de données : SQLite, un simple fichier db.sqlite3. Zéro installation.
# ----------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ----------------------------------------------------------------------
# Mots de passe : règles de robustesse appliquées à la création d'un compte.
# ----------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ----------------------------------------------------------------------
# Langue et fuseau horaire
# ----------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True


# ----------------------------------------------------------------------
# Fichiers statiques (CSS, images)
# ----------------------------------------------------------------------
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ----------------------------------------------------------------------
# Django REST Framework
# ----------------------------------------------------------------------
REST_FRAMEWORK = {
    # Comment DRF identifie l'utilisateur d'une requête. Il essaie dans l'ordre :
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 1. un jeton JWT dans l'en-tête « Authorization: Bearer <jeton> »
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        # 2. une session Django (pratique pour tester dans l'interface navigable de DRF)
        "rest_framework.authentication.SessionAuthentication",
    ],
    # Règle par défaut si une vue ne précise rien :
    # tout le monde peut lire, seuls les connectés peuvent écrire.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    # Pagination : 10 résultats par page, avec des liens « next » / « previous ».
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}


# ----------------------------------------------------------------------
# Simple JWT : durée de vie des jetons
# ----------------------------------------------------------------------
SIMPLE_JWT = {
    # Jeton d'accès court : s'il est volé, il n'est utilisable qu'une heure.
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    # Jeton de rafraîchissement : permet de regénérer un access sans se reconnecter.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    # Le préfixe attendu dans l'en-tête HTTP : « Authorization: Bearer <jeton> ».
    "AUTH_HEADER_TYPES": ("Bearer",),
}
