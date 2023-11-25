import os

from flask import Flask
from flask_cors import CORS
from logging.config import dictConfig


log_level = os.environ.get('LOG_LEVEL') or 'DEBUG'

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': log_level,
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
CORS(app)