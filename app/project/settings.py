import os
from pathlib import Path
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')

# Define templates directory
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')


# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'condominium',
    'residents',
    'personalities',
    'parameters',
    'data_management',
    'reservations',
    'gatehouse',
    'administrative',
    'financial',
    'system',
    'email_service',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}

# Password validation
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
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
## STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Local onde você salva os arquivos estáticos durante o desenvolvimento
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static_src'),
]

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'condominium': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'residents': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'personalities': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

JAZZMIN_SETTINGS = {
    # Título da janela do navegador
    "site_title": "BrasilCondo Admin",
    
    # Título no brand do login (mobile e desktop)
    "site_header": "BrasilCondo",
    
    # Logo do seu site
    "site_brand": "BrasilCondo",
    
    # Caminho para o logotipo exibido na tela de login (relativo a STATIC_URL)
    "site_logo": "img/LogotipoVetor_011.png",
    
    # Mensagem de boas vindas na tela de login
    "welcome_sign": "Bem-vindo(a) ao Sistema BrasilCondo",

    # CSS customizado para aplicar o tema padrão do admin (antes do dark mode)
    "custom_css": "css/custom_admin.css",
    
    # JS customizado para adicionar ícone de login no menu Account
    "custom_js": "js/custom_admin_login_icon.js",
    
    # Copyright no rodapé (Footer)
    "copyright": "BrasilCondo Ltda",
    "allrights_reserved": "Todos os direitos reservados.",
    
    # Revert to previous dark-ish theme (Jazzmin default variant)
    "theme": "darkly",
        
    # Menu lateral
    "show_sidebar": True,
    "navigation_expanded": True,
    
    # Ícones para os apps (FontAwesome)
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "condominium.Condominium": "fas fa-building",
        "condominium.Types_collaborators": "fa-solid fa-anchor-circle-exclamation",
        "condominium.Collaborators": "fa-solid fa-person-half-dress",
        "condominium.DocumentCondominium": "fa-solid fa-file-invoice",
        "parameters.Addresses": "fas fa-map-marked-alt",
        "parameters.States": "fas fa-flag",
        "parameters.TypesCondominium": "fas fa-home",
        "parameters.StructionCondominium": "fas fa-sitemap",
        "parameters.TypesVisitorRestrictions": "fa-solid fa-triangle-exclamation",
        "residents.CondominiumUnit": "fas fa-building",
        "residents.Resident": "fas fa-user-tie",
        "residents.Vehicle": "fas fa-car",
        "residents.Emergency": "fas fa-phone",
        "residents.Animal": "fas fa-dog",
        "residents.Visitor": "fas fa-user-friends",
        "residents.RealEstateAgency": "fas fa-home",
        "residents.Documents": "fa-solid fa-bag-shopping",
        "personalities.Entity": "fa-solid fa-boxes-stacked",
        "personalities.BusinessSector": "fa-solid fa-chess",
        "data_management.ImportModule": "fas fa-file-import",
        "data_management.ExportModule": "fas fa-file-export",
        "data_management.LogModule": "fas fa-list",
        "data_management.AuditModule": "fas fa-history",
        "data_management.ScheduledTaskModule": "fa-regular fa-calendar-days",
        "data_management.IntegrationModule": "fas fa-plug",
        "data_management.BackupModule": "fas fa-save",
        "data_management.RestoreModule": "fas fa-undo",
        "reservations.Rentals": "fa-solid fa-location-arrow",
        "reservations.MaintenanceReservations": "fas fa-tools",
        "reservations.MoveReservations": "fas fa-truck-moving",
        "reservations.Reforms": "fas fa-hammer",
        "gatehouse.Shift": "fa-solid fa-sun",
        "gatehouse.ServiceTransition": "fa-solid fa-people-arrows",
        "gatehouse.UsefulPhoneNumber": "fa-solid fa-phone",
        "gatehouse.Order": "fa-solid fa-box",
        "gatehouse.VisitorsRegister": "fa-solid fa-clipboard-list",
        "gatehouse.Correspondence": "fa-solid fa-envelope",
        "gatehouse.Occurrence": "fa-solid fa-hands-asl-interpreting",
        "gatehouse.Bag": "fa-solid fa-suitcase-rolling",
        "gatehouse.ElectronicTimeClock": "fa-solid fa-clipboard",
        "administrative.Bank": "fas fa-university",
        "administrative.Circular": "fas fa-bullhorn",
        "administrative.Contract": "fas fa-file-contract",
        "administrative.Infraction": "fas fa-gavel",
        "administrative.Meter": "fas fa-tachometer-alt",
        "administrative.Notification": "fas fa-bell",
        "administrative.Patrimony": "fas fa-archway",
        "administrative.BudgetForecast": "fas fa-chart-line",
        "administrative.ChartOfAccount": "fas fa-chart-pie",
        "administrative.Project": "fas fa-project-diagram",
        "administrative.Task": "fas fa-tasks",
        "administrative.VirtualAssembly": "fa-solid fa-elevator",
        "financial.Agreement": "fas fa-handshake",
        "financial.PaymentSlip": "fas fa-file-invoice-dollar",
        "financial.Cash": "fas fa-cash-register",
        "financial.Collection": "fas fa-coins",
        "financial.Shopping": "fas fa-shopping-cart",
        "financial.Loan": "fas fa-hand-holding-usd",
        "financial.NewRelease": "fas fa-money-bill-wave",
        "financial.Payment": "fas fa-credit-card",
        "financial.Apportionment": "fa-solid fa-chart-pie",
        "financial.Receipt": "fas fa-receipt",
        "financial.BankTransfer": "fa-solid fa-square-poll-horizontal",
        "system.TechnicalSupportTicket": "fas fa-wrench",
        "system.EmailConfiguration": "fas fa-envelope",
        "system.SMSConfiguration": "fas fa-sms",
        "system.WhatsAppSettings": "fa-solid fa-message",
        "system.SystemLog": "fas fa-file-alt",
        "system.AutomatedRoutine": "fas fa-robot",
        "system.Training": "fas fa-chalkboard-teacher",
        "system.IntegrationToken": "fas fa-key",
        "system.ConnectedUser": "fas fa-user-friends",
        "email_service.SMTP_Settings": "fas fa-envelope",
        "email_service.UsageProfiles": "fas fa-user-friends",
        "email_service.ShippingQueue": "fas fa-truck",
        "email_service.EmailHistory": "fas fa-history",
    },
    
    "show_ui_builder": False,
}


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "default_theme_mode": "dark",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
