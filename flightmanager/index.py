import cloudinary.uploader

from flightmanager import app, utils, login
from flask import render_template, request, redirect, url_for
from flightmanager.models import UserRole
from flask_login import login_user
from flightmanager.admin import *


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/user-register', methods=['get', 'post'])
def user_register():
    err_msg = ''
    if request.args.__eq__('POST'):
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        date_of_birth = request.form.get('date_of_birth')
        identity_card = request.form.get('identity_card')
        nationality = request.form.get('nationality')
        address = request.form.get('address')
        phone = request.form.get('phone')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.args.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                    return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi:' + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_login():
    msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        login_user(user=user)
        next = request.args.get('next', 'home')
        return redirect(url_for(next))
    else:
        msg = 'Sai tên đăng nhập hoặc mật khẩu'

    return render_template('login.html', msg=msg)


@app.route('/user-logout')
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))


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
