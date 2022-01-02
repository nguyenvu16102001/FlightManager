from flightmanager import app, db
from flightmanager.models import *
import hashlib


def get_account_by_id(account_id):
    return Account.query.get(account_id)


def check_login(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()


def get_user(first_name, last_name, identity_card):
    user = User.query.filter(User.first_name.contains(first_name), User.last_name.contains(last_name), User.identity_card.__eq__(identity_card)).first()

    return user


def add_user(first_name, last_name, gender, date_of_birth, identity_card, nationality, avatar, address, phone, email):
    user = User(first_name=first_name,
                last_name=last_name,
                gender=gender,
                date_of_birth=date_of_birth,
                identity_card=identity_card,
                nationality=nationality,
                avatar=avatar,
                address=address,
                phone=phone,
                email=email)
    db.session.add(user)
    db.session.commit()


def add_customer(user_id, mileage_acquired=0):
    customer = Customer(user_id=user_id, mileage_acquired=mileage_acquired)
    db.session.add(customer)
    db.session.commit()


def add_acccount(user_id, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    account = Account(user_id=user_id, username=username.strip(), password=password)
    db.session.add(account)
    db.session.commit()


def register_customer(first_name, last_name, gender, date_of_birth, identity_card, nationality, avatar, address, phone, email, username, password):
    add_user(first_name=first_name, last_name=last_name, gender=gender, date_of_birth=date_of_birth,
             identity_card=identity_card, nationality=nationality, avatar=avatar,
             address=address, phone=phone, email=email)

    user = get_user(first_name=first_name, last_name=last_name, identity_card=identity_card)

    add_customer(user_id=user.user_id)

    add_acccount(user_id=user.user_id, username=username, password=password)
