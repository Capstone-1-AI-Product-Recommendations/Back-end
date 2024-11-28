"""
Django settings for web_backend project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-+7t4hvz!@5#(_p)qk)7v4z^c!42=kky2sokrefs$&rv7=%9q6g"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

SITE_ID = 1
# Application definition

INSTALLED_APPS = [
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    'carts',
    'products',
    'admin_dashboard',
    'orders',
    'payments',
    'recommendations',
    'seller_dashboard',
    'django.contrib.sites',           
    'rest_framework.authtoken',
    'dj_rest_auth',
    "dj_rest_auth.registration",
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', 
    'social_django',
    "web_backend",
    'corsheaders',
    'cloudinary',
    'cloudinary_storage',    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'web_backend.middleware.UserActivityLoggerMiddleware',
]
CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "web_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600

WSGI_APPLICATION = "web_backend.wsgi.application"

GOOGLE_CLIENT_ID = '591294797278-10rip37g7755at0eg17r5nj1rbk61m4a.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:8000/api/auth/callback/'


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "email",
            "profile",
        ],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            'client_id' : GOOGLE_CLIENT_ID,
            'secret' : GOOGLE_CLIENT_SECRET,
            'key' : ''
        }
        
    }
}

# Cấu hình Cloudinary
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dkleeailh',
    'API_KEY': '171326873511271',
    'API_SECRET': 'aIwwnuXsnlhQYM0VsavcR_l56kQ'
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
# CLOUD_NAME = 'dkleeailh'
# API_KEY = '171326873511271'
# API_SECRET = 'aIwwnuXsnlhQYM0VsavcR_l56kQ'

# REST_USE_JWT = True
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {  
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'web_backend',
        'USER': 'root',
        'PASSWORD': 'nhc171103',
        'HOST': 'localhost',
        'PORT': '3306', 
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static')
]
MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR,'media')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [        
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
        # 'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.JSONParser',
    ],
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',  
    'http://127.0.0.1:8000/api/auth/registration/google/'
]
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:8000',  
]

EMAIL_HOST = 'smtp.gmail.com'  # Máy chủ SMTP của Gmail
EMAIL_PORT = 587  # Cổng SMTP cho Gmail
EMAIL_USE_TLS = True  # Sử dụng TLS
EMAIL_HOST_USER = 'aiproductrecommendation@gmail.com'  # Email của bạn
EMAIL_HOST_PASSWORD = 'fhow btav zjjr gthc'  # Mật khẩu email
DEFAULT_FROM_EMAIL = 'E-commerce <aiproductrecommendation@gmail.com>'

