"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.2.10.

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
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # add

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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    'allauth.account.auth_backends.AuthenticationBackend',  # django-allauth
)

ACCOUNT_AUTHENTICATION_METHOD = 'email'   # email+パスワード認証方式を指定
ACCOUNT_USERNAME_REQUIRED = False         # ユーザ名を利用しない設定にする
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # CustomUserモデルにusernameは無い

SITE_ID = 1  # django-allauthを利用する際に必要な設定
LOGIN_REDIRECT_URL = 'VisualizingTweets:index'   # ログインURLの設定
LOGIN_URL = 'account_login'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'  # ログアウトリダイレクトの設定
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # ユーザ登録確認メールを送信する
ACCOUNT_EMAIL_REQUIRED = True  # メールアドレスを必須項目に指定
ACCOUNT_LOGOUT_ON_GET = True   # ログアウトリンクのクリック一発でログアウトする設定

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # コンソール上にメッセージを表示

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

# humanize settings
NUMBER_GROUPING = 3
