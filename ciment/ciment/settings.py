"""
Django settings for Dangote Cement project.
Dangote Cement - Material Reception System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================== CONFIGURATION DE BASE ====================

# Environnement (development/production)
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

# Clé secrète
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'clé-par-défaut-pour-dev-seulement')

# Mode debug selon l'environnement
DEBUG = (DJANGO_ENV == 'development')

# Hôtes autorisés selon l'environnement
if DJANGO_ENV == 'production':
    ALLOWED_HOSTS = ['ton-domaine.com', 'www.ton-domaine.com', '127.0.0.1']
    print("Mode PRODUCTION active")
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.8.119', '*']
    print("Mode DEVELOPPEMENT active")


# ==================== APPLICATIONS ====================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    
    # Third-party apps
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'users.apps.UsersConfig',
    'contracts.apps.ContractsConfig',
    'suppliers.apps.SuppliersConfig',
    'evaluations.apps.EvaluationsConfig',
    'dashboard.apps.DashboardConfig',
    'reports.apps.ReportsConfig',
    'orders.apps.OrdersConfig',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Middleware personnalisé pour la sécurité
    'ciment.middleware.NoCache',
    'ciment.middleware.SessionSecurityMiddleware',
]

ROOT_URLCONF = 'ciment.urls'


# ==================== TEMPLATES ====================

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

WSGI_APPLICATION = 'ciment.wsgi.application'


# ==================== BASE DE DONNÉES ====================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'dangote_db'),
        'USER': os.getenv('DB_USER', 'cement_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'aime'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# ==================== VALIDATION MOTS DE PASSE ====================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==================== INTERNATIONALISATION ====================

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# ==================== FICHIERS STATIQUES ====================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================== AUTHENTIFICATION ====================

AUTH_USER_MODEL = 'users.User'
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:login'
LOGOUT_REDIRECT_URL = 'users:login'

# Configuration de Session - Sécurité
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 heure
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Cache Control - Empêcher le cache des pages protégées
CACHE_MIDDLEWARE_SECONDS = 0

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==================== CONFIGURATION EMAIL ====================

# Configuration email unifiée pour dev et prod
# Les emails seront envoyés via Gmail SMTP dans les deux cas
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# Pour déboguer les emails en développement (optionnel)
if DJANGO_ENV == 'development':
    # Afficher les emails dans la console en plus de les envoyer
    import logging
    logging.getLogger('django.core.mail').setLevel(logging.DEBUG)

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Dangote Cement - Material Reception <noreply@dangote.com>')

# URL du site (pour les liens dans les emails)
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
SITE_NAME = os.getenv('SITE_NAME', 'Dangote Cement - Material Reception System')

# Activer/désactiver les notifications email
ENABLE_EMAIL_NOTIFICATIONS = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() in ('true', '1', 'yes')


# ==================== SÉCURITÉ PRODUCTION ====================

if DJANGO_ENV == 'production':
    # Sécurité renforcée
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # HTTPS Strict Transport Security
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Protection CSRF
    CSRF_TRUSTED_ORIGINS = [
        'https://ton-domaine.com',
        'https://www.ton-domaine.com',
    ]
    
    # Optimisation des performances
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
