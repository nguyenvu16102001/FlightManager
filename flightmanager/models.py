from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from flightmanager import db
from flask_login import UserMixin
from _datetime import datetime
from enum import Enum as UserEnum


class UserRole(UserEnum):
    CUSTOMER = 1
    EMPLOYEE = 2
    ADMIN = 3


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class Account(BaseModel, UserMixin):
    __tablename__ = 'account'
    username = Column(String(20), nullable=False)
    password = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    join_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole, default=UserRole.CUSTOMER))


if __name__ == '__main__':
    # db.create_all()
    acount1 = Account(username = 'admin', password = '202cb962ac59075b964b07152d234b70', user_role = UserRole.ADMIN)
    acount2 = Account(username='user', password='202cb962ac59075b964b07152d234b70')
    db.session.add(acount1)
    db.session.add(acount2)
    db.session.commit()