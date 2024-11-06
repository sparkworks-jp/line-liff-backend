import os
from .base import *

DATABASES = {
     'default': {
        'ENGINE': 'django.db.backends.postgresql',  
        'NAME': 'naruto',  
        'USER': 'postgres',  
        'PASSWORD': 'Tzk7jN1KhNsGP5Gy', 
        'HOST': 'prod-db-instance.cvegir20ptgl.ap-northeast-1.rds.amazonaws.com',  
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
            'formatter': 'levelname_message'
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

# os.environ['AWS_ENDPOINT_URL_S3'] = 
# os.environ['AWS_ACCESS_KEY_ID'] = 
# os.environ['AWS_SECRET_ACCESS_KEY'] = 
# os.environ['S3_BUCKET_NAME'] = 
