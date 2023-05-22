# -*- coding: utf-8 -*-
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

from config.config import DBConfig, AuthConfig

# Populate ENV vars from .env file.
load_dotenv()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    ROOT_DIR = Path(__file__).parent

    app.config.from_object(DBConfig())
    app.config.from_object(AuthConfig())
    app.config.from_prefixed_env()

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(ROOT_DIR / app.config['DB_RELATIVE_PATH'])

    db.init_app(app)

    login = LoginManager(app)
    login.login_view = "auth.login"

    @login.user_loader
    def load_user(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user

    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    from .auth import auth as auth_blueprint, auth_cli as auth_cli_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(auth_cli_blueprint)

    from .voting import voting as voting_blueprint
    app.register_blueprint(voting_blueprint)

    from .cli import goodvotes_cli as goodvotes_cli_blueprint
    app.register_blueprint(goodvotes_cli_blueprint)

    return app


from .cli import cli
from .voting import views
from .auth import views, cli, User
