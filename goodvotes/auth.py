# -*- coding: utf-8 -*-
from hashlib import sha256


def password_hash(passwd, salt):
    tmp = passwd + " " + salt
    return sha256(tmp.encode('utf-8')).hexdigest()
