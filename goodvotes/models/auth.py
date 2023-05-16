# -*- coding: utf-8 -*-
from goodvotes import *
import random
from time import sleep

from ..auth import password_hash


class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)

    def set_password(self, new_passwd):
        if len(new_passwd) > 40:
            raise Exception("Password must be no more than 40 chars")
        if len(new_passwd) < 8:
            raise Exception("Password must be at least 8 chars")
        self.password_hash = password_hash(new_passwd, self.salt)

    def check_password(self, passwd):
        return self.password_hash == password_hash(passwd, self.salt)

    def add_election(self, election):
        self.elections.append(election)

    def owns_election(self, eID):
        return eID in [e.eid for e in self.elections]
