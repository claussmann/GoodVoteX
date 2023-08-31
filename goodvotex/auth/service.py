# -*- coding: utf-8 -*-
from flask import flash
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from .models import User, Usergroup
from .. import db


def get_user(username):
    """

    :param username:
    :return: The user object with the given username (if exists).
    """
    return User.query.filter_by(username=username).first()

def get_group(groupname):
    """

    :param groupname:
    :return: The usergroup object with the given name (if exists).
    """
    return Usergroup.query.filter_by(name=groupname).first()

def register_user(username, name, email, password, group):
    """
    Registers a new user.

    :param email:
    :param username:
    :param name:
    :param password:
    :return: When registration successful, returns the user object.
    """
    u = User(username=username, name=name, email=email, group=group,
             password_hash=generate_password_hash(password, method='pbkdf2:sha512'))
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("The username is already taken")
        raise Exception
    return u

def register_group(groupname, displayname):
    """
    Registers a new group.

    :param groupname:
    :param displayname:
    :return: When registration successful, returns the group object.
    """
    group = Usergroup(name=groupname, displayname=displayname)
    db.session.add(group)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("The group name is already taken")
        raise Exception
    return group

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
