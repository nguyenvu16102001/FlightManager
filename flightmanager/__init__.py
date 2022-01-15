from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import cloudinary

app = Flask(__name__)
app.secret_key = '@(#)!@_!_#)!lda@)!('

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:0969573528At@localhost/flightmanager?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(
    cloud_name='dufpogfsu',
    api_key='432288691878876',
    api_secret='d4_eNXlXd077dziEKMJiQr8dWg4'
)
