import sqlite3
import uuid
import hashlib
from functools import wraps

from flask import request, Response


class PasswordManager:

    def __init__(self, dbfile='rpc-passwords.db', sha256_rounds=1000000, pepper='2fde251d-33fd-42c8-bdd9-8ac7788d5f5a'):
        self.sha256_rounds = sha256_rounds
        self.pepper = pepper

        self.conn = sqlite3.connect(dbfile, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS passwords (username text, passhash blob, salt text)')
        self.conn.commit()

    def register(self, username, password):
        self.cursor.execute('SELECT * FROM passwords WHERE username=?', (username,))
        if self.cursor.fetchone():
            raise UserPresentException()

        salt = str(uuid.uuid4())
        spice = salt + self.pepper
        passhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), spice.encode('utf-8'), self.sha256_rounds)

        self.cursor.execute('INSERT INTO passwords VALUES (?, ?, ?)', (username, passhash, salt))
        self.conn.commit()

    def check_auth(self, username, password):
        self.cursor.execute('SELECT * FROM passwords WHERE username=?', (username,))
        entry = self.cursor.fetchone()
        if entry:
            username, passhash, salt = entry
            spice = salt + self.pepper
            return passhash == hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), spice.encode('utf-8'), self.sha256_rounds)
        else:
            return False

    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.check_auth(auth.username, auth.password):
                return self.authenticate()
            return f(*args, **kwargs)
        return decorated

    @staticmethod
    def authenticate():
        """Sends a 401 response that enables basic auth"""
        return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

class UserPresentException(Exception):
    pass
