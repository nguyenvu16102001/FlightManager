import cloudinary.uploader
from flightmanager import app, utils, login
from flask import render_template, request, redirect, url_for
from flightmanager.models import UserRole
from flask_login import login_user, login_required, logout_user
from flightmanager.admin import *


@app.route('/')
def home():
    airports = utils.get_list_airport()
    return render_template('index.html', airports=airports)


@app.route('/ticket-sales')
def ticket_sales():
    return render_template('ticket_sales.html')


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ''
    if request.method.__eq__('POST'):
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
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
            if password.strip().__eq__(confirm):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                utils.register_customer(last_name=last_name, first_name=first_name, gender=gender,
                                        date_of_birth=date_of_birth, identity_card=identity_card,
                                        nationality=nationality, avatar=avatar_path, address=address,
                                        phone=phone, email=email, username=username, password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi:' + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['get', 'post'])
def user_login():
    err_msg = ''
    username = ''
    password = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            if user.user_role == None:
                login_user(user=user)
                next = request.args.get('next', 'home')
                return redirect(url_for(next))
            else:
                err_msg = 'Đăng nhập bằng tài khoản khách hàng'
        else:
            err_msg = 'Sai tên đăng nhập hoặc mật khẩu'

    return render_template('user_login.html', err_msg=err_msg)


@app.route('/user-logout')
def user_logout():
    logout_user()
    name = request.args.get('name')
    return redirect(url_for(name))


@app.route('/admin-login', methods=['post'])
def admin_login():
    err_msg = ''
    username = request.form.get('username')
    password = request.form.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        if user.user_role == UserRole.ADMIN:
            login_user(user=user)
        else:
            err_msg = 'Hãy đăng nhập bằng tài khoản admin'

    return redirect('/admin')


@app.route('/employee_login', methods=['get', 'post'])
def employee_login():
    err_msg = ''
    username = ''
    password = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

    user = utils.check_login(username=username, password=password)
    if user:
        if user.user_role == UserRole.EMPLOYEE:
            login_user(user=user)
            next = request.args.get('next', 'ticket_sales')
            return redirect(url_for(next))
        else:
            err_msg = 'Đăng nhập bằng tài khoản nhân viên'
    else:
        err_msg = 'Sai tên đăng nhập hoặc mật khẩu'

    return render_template('ticket_sales.html', err_msg=err_msg)


@app.route('/flight-selection')
def flight_selection():
    departure_airport = request.args.get("departure_airport")
    arrival_airport = request.args.get("arrival_airport")
    departure_day = request.args.get("departure_day")
    flight = None
    if departure_airport and arrival_airport and departure_day:
        flight = utils.get_flight_status(departure_airport=departure_airport, arrival_airport=arrival_airport,
                                         departure_day=departure_day)

    return render_template('flight_selection.html', flight=flight)


@app.route('/flight-status')
def flight_status():
    airports = utils.get_list_airport()
    departure_airport = request.form.get('departure_airport')
    arrival_airport = request.form.get('arrival_airport')
    departure_day = request.form.get('departure_day')
    if departure_airport and arrival_airport and departure_day:
        status = utils.get_flight_status(departure_airport=departure_airport, arrival_airport=arrival_airport,
                                         departure_day=departure_day)
        return redirect('flight_status.html', status=status)

    return render_template('flight_status.html', airports=airports)


@app.route('/flight-scheduling')
@login_required
def flight_scheduling():
    err_msg = ''
    airplanes = utils.get_list_airplane()
    airports = utils.get_list_airport()
    regulations = utils.get_regulations_by_id(regulations_id=1)
    flight_id = request.args.get('flight_id')
    if flight_id:
        airplane_id = request.args.get('airplane_id')
        departure_airport = request.args.get('departure_airport')
        arrival_airport = request.args.get('arrival_airport')
        departure_day = request.args.get('departure_day')
        flight_time = request.args.get('flight_time')
        business_class = request.args.get('business_class')
        economy_class = request.args.get('economy_class')
        transit_airports = []
        timing_points = []
        notes = []
        for i in range(regulations.maximum_number_of_intermediate_airports):
            if request.args.get('transit_airport' + str(i)):
                transit_airports.append(request.args.get('transit_airport' + str(i)))
                timing_points.append(request.args.get('timing_point' + str(i)))
                notes.append(request.args.get('note' + str(i)))

        try:
            utils.flight_scheduling(flight_id=flight_id, airplane_id=airplane_id, departure_airport=departure_airport,
                                    arrival_airport=arrival_airport, departure_day=departure_day,
                                    flight_time=flight_time, business_class=business_class, economy_class=economy_class,
                                    transit_airports=transit_airports, timing_points=timing_points, notes=notes)
            flight = utils.get_flight_by_id(flight_id=flight_id)
            if flight:
                err_msg = 'Thêm thành công'
            else:
                err_msg = 'Thêm thất bại'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi:' + str(ex)

    return render_template('flight_scheduling.html', airplanes=airplanes, airports=airports,
                           regulations=regulations, err_msg=err_msg)


@login.user_loader
def load_user(account_id):
    return utils.get_account_by_id(account_id=account_id)


if __name__ == '__main__':
    app.run(debug=True)
