import os

from dotenv import load_dotenv
from lib.flask import app
from lib.flask.routes import init_routes

load_dotenv()

if __name__ == "__main__":
    init_routes()

    port = int(os.environ.get('PORT')) or 5000
    app.run(host="0.0.0.0", port=port, debug=True)