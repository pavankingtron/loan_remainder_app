from flask import Flask
from app.config import Config
from app.extensions import db
from dotenv import load_dotenv

load_dotenv()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # 🔥 FORCE DB INIT BEFORE FIRST REQUEST
    @app.before_first_request
    def create_tables():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app
