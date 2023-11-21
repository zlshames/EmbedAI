from dotenv import load_dotenv
from lib.flask import app
from lib.flask.routes import init_routes

load_dotenv()

if __name__ == "__main__":
    init_routes()
    app.run(host="0.0.0.0", debug=True)