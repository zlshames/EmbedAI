import os

from dotenv import load_dotenv
from .lib.flask import app
from .lib.flask.routes import init_routes

load_dotenv()

def main():
    init_routes()

    port = int(os.environ.get('PORT', '5000'))
    env = os.environ.get('ENV', 'production')
    app.run(host="0.0.0.0", port=port, debug=True if env == 'development' else False)