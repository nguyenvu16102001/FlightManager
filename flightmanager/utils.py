from flightmanager import app, db
from flightmanager.models import *
import hashlib


def get_user_by_id(user_id):
    return Account.query.get(user_id)


def check_login(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()