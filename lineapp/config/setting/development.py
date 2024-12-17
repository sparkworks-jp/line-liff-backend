import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

# CROS
CORS_ALLOW_ALL_ORIGINS = True  
CORS_ALLOW_CREDENTIALS = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql',  
        'NAME': os.environ['NARUTO_DB_NAME'],
        'USER': os.environ['NARUTO_DB_USER'],
        'PASSWORD': os.environ['NARUTO_DB_PASSWORD'],
        'HOST': os.environ['NARUTO_DB_HOST'],
        'PORT': '5432',  
        'OPTIONS': {
            'options': '-c search_path=line'
        },
        'TEST': {
            'NAME': 'test_naruto',  
            'OPTIONS': {
                'options': '-c search_path=line,public', 
            },
        },
    }
}
WSGI_APPLICATION = 'config.wsgi.application'

# 実行SQLを標準出力に出力する
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'levelname_message': {
            'format': '{asctime} {process} {thread} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'levelname_message'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}





# paypay
PAYPAY_IP_WHITELIST = "13.112.237.64,52.199.148.9,54.199.212.149,13.208.106.122,13.208.115.200,13.208.152.196" 




