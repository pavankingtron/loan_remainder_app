from flask import Flask
from dotenv import load_dotenv
from app.config import Config
from app.extensions import db, mail

load_dotenv()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    # 🔥 IMPORT MODELS BEFORE CREATING TABLES
    from app import models

    with app.app_context():
        db.create_all()

    from app.routes import main
    app.register_blueprint(main)

    return app
