from flightmanager import app, utils, login
from flask import render_template, request, redirect
from flightmanager.models import UserRole
from flask_login import login_user
from flightmanager.admin import *


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin-login', methods=['post'])
def admin_login():
    msg = ''
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        if user.user_role == UserRole.ADMIN:
            login_user(user=user)
        else:
            msg = 'Hãy đăng nhập bằng tài khoản admin'

    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
