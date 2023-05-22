# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash

from .models import User
from .. import db


def get_user(username):
    """

    :param username:
    :return: The user object with the given username (if exists).
    """
    return User.query.filter_by(username=username).first()


def register_user(username, name, email, password):
    """
    Registers a new user.

    :param email:
    :param username:
    :param name:
    :param password:
    :return: When registration successful, returns the election object.
    """
    u = User(username=username, name=name, email=email,
             password_hash=generate_password_hash(password, method='pbkdf2:sha512'))
    db.session.add(u)
    db.session.commit()
    return u


def change_password(user, password, new_password, confirm_password, force=False):
    """
    Changes a user password.

    :param user:
    :param password:
    :param new_password:
    :param confirm_password:
    :param force: If True all checks are disabled and the `new_password` is set.
    :return:
    """
    if not force:
        if new_password != confirm_password:
            raise Exception("New passwords do not match.")
        if not user.check_password(password):
            raise Exception("Incorrect password!")
    user.set_password(new_password)
    db.sync_user(user.username)
