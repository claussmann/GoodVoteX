# -*- coding: utf-8 -*-
from flask import flash
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from .models import User
from .. import db


def get_user(username):
    """

    :param username:
    :return: The user object with the given username (if exists).
    """
    return User.query.filter_by(username=username).first()

def get_all_users():
    """

    :return: All user objects, sorted by username.
    """
    ret = User.query.all()
    return sorted(ret, key=lambda u: u.username)

def register_user(username, name, email, password):
    """
    Registers a new user.

    :param email:
    :param username:
    :param name:
    :param password:
    :return: When registration successful, returns the user object.
    """
    u = User(username=username, name=name, email=email,
             password_hash=generate_password_hash(password, method='pbkdf2:sha512'))
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("The username is already taken")
        raise Exception
    return u

def delete_user(username):
    User.query.filter_by(username=username).delete()
    db.session.commit()

def update_user_permissions(username, admin=None, create=None, vote=None):
    """
    Update permissions of username.

    :param admin: Set admin permission True/False (Optional)
    :param create: Set ability to create and manage own elections True/False (Optional)
    :param vote: Set voting ability to True/False (Optional)
    """
    u = get_user(username)
    u.update_permissions(admin=admin, create=create, vote=vote)
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
    db.session.add(user)
    db.session.commit()


def toggle_theme(user):
    """
    Changes a user's theme from light to dark or vice versa.

    :param user:
    :return:
    """
    if user.theme == "dark":
        user.theme = "light"
    else:
        user.theme = "dark"
    db.session.add(user)
    db.session.commit()
