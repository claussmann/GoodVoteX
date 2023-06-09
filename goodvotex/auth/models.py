from flask_login import UserMixin
from flask_sqlalchemy.model import Model
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(300), nullable=False)

    def set_password(self, new_passwd):
        if len(new_passwd) > 40:
            raise Exception("Password must be no more than 40 chars")
        if len(new_passwd) < 8:
            raise Exception("Password must be at least 8 chars")
        self.password_hash = generate_password_hash(new_passwd)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_election(self, election):
        self.elections.append(election)

    def owns_election(self, election):
        return election in self.elections
