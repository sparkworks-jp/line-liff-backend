import os
from .base import *

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
    }
}

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
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'levelname_message',
            'encoding': 'utf-8'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    },
}

# CROS
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True  
CORS_ALLOW_CREDENTIALS = True


# os.environ['AWS_ENDPOINT_URL_S3'] = 
# os.environ['AWS_ACCESS_KEY_ID'] = 
# os.environ['AWS_SECRET_ACCESS_KEY'] = 
# os.environ['S3_BUCKET_NAME'] = 
