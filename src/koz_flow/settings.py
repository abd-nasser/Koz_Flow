from pathlib import Path
import os 

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_$&duxxn#qq4b@^70$6ju1a)%&&igb0qh0%too1gigg%j_lai5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ----- LES NOUVEAUX PAQUETS (API) -----
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders', 
    
     # ----- NOS APPS (créées par nous) -----
    'home_app',
    'auth_app',         # Gère les utilisateurs (connexion, inscription)
    'client_app',       # Portail client
    'order_app',        # Panier et commandes
    'paiement_app',     # Paiements
    'products_app',     # Pièces détachées
    'vehicul_app',      # Catalogue voitures
    'directeur_app',    # Dashboard directeur
    'commercial_app',   # Dashboard commercial
    'chat_app',         # Messagerie client-commercial
    'leads_app',        # Demandes de crédit
    
    
    #tailwind_app
    "tailwind",
    "theme",
]

# ----- MIDDLEWARE (filtres qui s'exécutent à chaque requête) -----
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',# 👈 Doit être le PLUS HAUT
    # Pourquoi ? Parce qu'il doit traiter la requête AVANT les autres
    # Il ajoute les en-têtes CORS (Access-Control-Allow-Origin, etc.)
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ----- CONFIGURATION DE DRF (Django Rest Framework) -----
REST_FRAMEWORK = {
    # DEFAULT_AUTHENTICATION_CLASSES = comment on vérifie qu'un utilisateur est connecté
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # JWTAuthentication = regarde dans l'en-tête "Authorization" de la requête
     # Si le token JWT est valide, l'utilisateur est considéré comme connecté
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # DEFAULT_PERMISSION_CLASSES = qui à le droit d'appeler les APIs ?
    
    #pour désactiver CSRF sur les APIs
    
    #'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.TokenAuthentication',
    #),
   
    # IsAuthenticated = SEUL les utilisateurs connectés peuvent appeler l'API
    # Si tu n'es pas connecté → erreur 401 (Non autorisé)
}


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]


# ----- CONFIGURATION DES TOKENS JWT -----
from datetime import timedelta

SIMPLE_JWT = {
    #ACCES_TOKEN_LIFETIME
    # Après 60 minutes, le token expire et tu dois en demander un nouveau
    'ACCES_TOKEN_LIFETIME': timedelta(minutes=60),
    
    #REFRESH_TOKEN_LIFETIME
    # Pendant 7 jours, tu peux utiliser le refresh token pour obtenir un nouveau access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    #ROTATE_REFRESH_TOKENS
    #change les tokens à chaque refresh , plus de secur
    
    'ROTATE_REFRESH_TOKENS':True,
    
    #BLACKLIST_AFTER_ROTATION = True
    #les ancien tokens sont blacklisté plus reutilisable
    'BLACKLIST_AFTER_ROTATION': True,    
    
}

# ----- CONFIGURATION CORS (qui a le droit d'appeler nos APIs) -----
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",      # Ton site web en développement
    "http://127.0.0.1:8000",      # Pareil mais avec IP local
    #"https://kozservices.bf",     # Ton site web en production (quand il sera en ligne)
]

# CORS_ALLOW_CREDENTIALS = True
# Permet d'envoyer les cookies et les en-têtes d'authentification
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'koz_flow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR/"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'koz_flow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

#AUTHENTICATION
AUTH_USER_MODEL = "auth_app.kozUser"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = "media/"
STATIC_ROOT = os.path.join(BASE_DIR/"staticfiles")
MEDIA_ROOT = os.path.join(BASE_DIR/"media/")
STATICFILES_DIRS = [os.path.join(BASE_DIR/"koz_flow/static/")]

#Taiwlind configurations
TAILWIND_APP_NAME = "theme"
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"