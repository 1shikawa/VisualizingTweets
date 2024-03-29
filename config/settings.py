"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k)g9ls8wvxgg2^!yny89n4w5&46kfluk6&1dt^+wvrpkdqr$p!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',  # add
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize', # add

    'bootstrap4',  # add
    'accounts',  # add
    'VisualizingTweets',  # add
    'VisualizingYoutube',  # add

    'django.contrib.sites',  # add
    'allauth',  # add
    'allauth.account',  # add
    'allauth.socialaccount',  # add
    'allauth.socialaccount.providers.twitter',  # add
    'allauth.socialaccount.providers.google',  # add
    'allauth.socialaccount.providers.github'  # add
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

##########################
# django-allauth setting #
##########################
AUTH_USER_MODEL = 'accounts.CustomUser'

# django-allauthで利用するdjango.contrib.sitesを使うためにサイト識別用IDを設定
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    # 一般ユーザー用(メールアドレス認証)
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',  # 管理サイト用(ユーザー名認証)
)
# メールアドレス認証に変更する設定
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # CustomUserモデルにusernameは無い

# サインアップにメールアドレス確認を挟むよう設定
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True

# ログイン/ログアウト後の遷移先を設定
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'VisualizingTweets:index'
ACCOUNT_LOGOUT_REDIRECT_URL = 'VisualizingTweets:stock_list'

# ログアウトリンクのクリック一発でログアウトする設定
ACCOUNT_LOGOUT_ON_GET = True


#####################
# tweepyAPI setting #
#####################
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']


######################
# YoutubeAPI setting #
######################
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']


######################
# FanzaAPI setting #
######################
FANZA_API_ID = os.environ['FANZA_API_ID']
FANZA_AFFILIATE_ID = os.environ['FANZA_AFFILIATE_ID']

##########################
# Email SendGrid setting #
##########################
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # コンソール上にメッセージを表示
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
EMAIL_HOST = 'influencer-search.herokuapp.com'
DEFAULT_FROM_EMAIL = 'notify@influencer-search.herokuapp.com'
SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
SENDGRID_SANDBOX_MODE_IN_DEBUG = False


###################
# logging setting #
###################
LOGGING = {
    # バージョンは「1」固定
    'version': 1,
    # 既存のログ設定を無効化しない
    'disable_existing_loggers': False,
    # ログフォーマット
    'formatters': {
        # 開発用
        'develop': {
            'format': '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d '
                      '%(message)s'
        },
    },
    # ハンドラ
    'handlers': {
        # コンソール出力用ハンドラ
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'develop',
        },
    },
    # ロガー
    'loggers': {
        # 自作アプリケーション全般のログを拾うロガー
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Django本体が出すログ全般を拾うロガー
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # 発行されるSQL文を出力するための設定
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
    },
}

#####################
# humanize settings #
#####################
NUMBER_GROUPING = 3


#####################
# JAZZMIN settings #
#####################
JAZZMIN_SETTINGS = {
    # title of the window
    'site_title': 'Influencer-Search管理サイト',

    # Title on the brand, and the login screen (19 chars max)
    'site_header': 'Influencer-Search',

    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    # 'site_logo': 'polls/img/logo.png',

    # Welcome text on the login screen
    'welcome_sign': 'Welcome to Influencer-Search',

    # Copyright on the footer
    # 'copyright': 'Acme Ltd',

    # The model admin to search from the search bar, search bar omitted if excluded
    # 'search_model': 'auth.User',
    'search_model': 'accounts.CustomUser',

    # Field name on user model that contains avatar image
    'user_avatar': None,

    ############
    # Top Menu #
    ############

    # Links to put along the top menu
    'topmenu_links': [

        # Url that gets reversed (Permissions can be added)
        {'name': 'Home',  'url': 'admin:index',
            'permissions': ['accounts.view_user']},

        # external url that opens in a new window (Permissions can be added)
        # {'name': 'Support', 'url': 'https://github.com/farridav/django-jazzmin/issues', 'new_window': True},

        # model admin to link to (Permissions checked against model)
        # {'model': 'auth.User'},
        {'model': 'accounts.CustomUser'},

        # App with dropdown menu to all its models pages (Permissions checked against models)
        {'app': 'Stock'},
    ],

    #############
    # User Menu #
    #############

    # Additional links to include in the user menu on the top right ('app' url type is not allowed)
    'usermenu_links': [
        # {'name': 'Support', 'url': 'https://github.com/farridav/django-jazzmin/issues', 'new_window': True},
        # {'model': 'auth.user'}
        # {'model': 'accounts.CustomUser'}
    ],

    #############
    # Side Menu #
    #############

    # Whether to display the side menu
    'show_sidebar': True,

    # Whether to aut expand the menu
    'navigation_expanded': True,

    # Hide these apps when generating side menu e.g (auth)
    'hide_apps': [],

    # Hide these models when generating side menu (e.g auth.user)
    'hide_models': [],

    # List of apps to base side menu ordering off of (does not need to contain all apps)
    'order_with_respect_to': ['accounts', 'polls'],

    # Custom links to append to app groups, keyed on app name
    # 'custom_links': {
    #     'polls': [{
    #         'name': 'Make Messages',
    #         'url': 'make_messages',
    #         'icon': 'fas fa-comments',
    #         'permissions': ['polls.view_poll']
    #     }]
    # },

    # Custom icons for side menu apps/models See https://www.fontawesomecheatsheet.com/font-awesome-cheatsheet-5x/
    # for a list of icon classes
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
    },
    # Icons that are used when one is not manually specified
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {"accounts.CustomUser": "collapsible", "accounts.group": "vertical_tabs", },
}


###################
# heroku settings #
###################
import dj_database_url
DATABASES['default'] = dj_database_url.config()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ['*']
# STATIC_ROOT = 'staticfiles'
DEBUG = False

try:
    from .local_settings import *
except ImportError:
    pass


import django_heroku
django_heroku.settings(locals())

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


