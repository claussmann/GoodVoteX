# -*- coding: utf-8 -*-
import random
from time import sleep

from ...auth import password_hash


class User:
    def __init__(self, username, name, password):
        self.password_hash = None
        if len(name) > 60:
            raise Exception("Name is too long.")
        if len(name) < 3:
            raise Exception("Name is too short.")
        self.name = name
        self.salt = "%08x" % random.randint(0, 0xFFFFFFFF)
        self.username = username.lower()
        self.elections = list()
        self.set_password(password)

    def set_password(self, new_passwd):
        if len(new_passwd) > 40:
            raise Exception("Password must be no more than 40 chars")
        if len(new_passwd) < 8:
            raise Exception("Password must be at least 8 chars")
        self.password_hash = password_hash(new_passwd, self.salt)

    def check_password(self, passwd):
        sleep(0.001 * random.randint(1, 2000))  # prevent timing attacks
        return self.password_hash == password_hash(passwd, self.salt)

    def add_election(self, election):
        self.elections.append(election)

    def serialize(self):
        ret = {
            "name": self.name,
            "username": self.username,
            "salt": self.salt,
            "password_hash": self.password_hash,
            "elections": [e.eid for e in self.elections]
        }
        return ret

    def owns_election(self, eID):
        return eID in [e.eid for e in self.elections]
