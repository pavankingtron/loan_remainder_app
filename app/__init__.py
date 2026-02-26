from flask import Flask
from dotenv import load_dotenv
from app.config import Config
from app.extensions import db, mail

load_dotenv()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    mail.init_app(app)

    # Create tables
    @app.before_first_request
    def create_tables():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app
