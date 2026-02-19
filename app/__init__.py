from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder="../templates",
                static_folder="../static")
    app.config["SECRET_KEY"] = "mysecretkey123"

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///payments.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize DB
    db.init_app(app)
    with app.app_context():
        db.create_all()
    from app.routes import main
    app.register_blueprint(main)

    return app
