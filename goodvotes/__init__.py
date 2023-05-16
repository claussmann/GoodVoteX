# -*- coding: utf-8 -*-
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
from ruamel.yaml import YAML
from flask_sqlalchemy import SQLAlchemy

from config.config import DBConfig, AuthConfig

# Populate ENV vars from .env file.
load_dotenv()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    ROOT_DIR = Path(__file__).parent

    deployment_type = 'prod' if app.config["DEBUG"] is False else 'dev'
    app.config.from_object(DBConfig())
    app.config.from_object(AuthConfig())
    app.config.from_prefixed_env()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(ROOT_DIR / app.config['DB_RELATIVE_PATH'])

    db.init_app(app)

    login = LoginManager(app)
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(id):
        user = db.get_user(id)
        return user

    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from .voting import voting as voting_blueprint

    app.register_blueprint(voting_blueprint)

    return app


from .voting import views
from .auth import views
