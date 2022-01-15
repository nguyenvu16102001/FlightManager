import cloudinary.uploader
from flightmanager import app, utils, login
from flask import render_template, request, redirect, url_for
from flightmanager.models import UserRole
from flask_login import login_user, login_required, logout_user
from flightmanager.admin import *
import uuid


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
    airports = utils.get_list_airport()
    ticket_prices = utils.get_list_ticket_price()
    departure_airport = request.args.get("departure_airport")
    arrival_airport = request.args.get("arrival_airport")
    departure_day = request.args.get("departure_day")
    flight = None
    if departure_airport and arrival_airport and departure_day:
        flight = utils.get_flight_status(departure_airport=departure_airport, arrival_airport=arrival_airport,
                                         departure_day=departure_day)

    return render_template('flight_selection.html', flight=flight, airports=airports, ticket_prices=ticket_prices)


flight_id = None
ticket_type = None


@app.route('/passengers', methods=['get', 'post'])
def passenger():
    err_msg = ''
    user_id = None
    global flight_id
    global ticket_type
    if request.args.get('flight_id'):
        flight_id = request.args.get('flight_id')
    if request.args.get('ticket_type'):
        ticket_type = request.args.get('ticket_type')
    if request.method.__eq__('POST'):
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        gender = request.form.get('gender')
        date_of_birth = request.form.get('date_of_birth')
        identity_card = request.form.get('identity_card')
        nationality = request.form.get('nationality')
        phone = request.form.get('phone')
        email = request.form.get('email')
        try:
            user = utils.get_user(identity_card)
            if user:
                user_id = user.user_id
                return redirect(url_for('seat_selection', user_id=user_id))
            else:
                utils.add_user(last_name=last_name, first_name=first_name, gender=gender, date_of_birth=date_of_birth,
                               identity_card=identity_card, nationality=nationality, address='', avatar='', phone=phone,
                               email=email)
                user = utils.get_user(identity_card=identity_card)
                if user:
                    user_id = user.user_id
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi:' + str(ex)

    return render_template('passengers.html', err_msg=err_msg)


@app.route('/seat_selection')
def seat_selection():
    user_id = request.args.get('user_id')
    seats = utils.get_seats(flight_id=flight_id, seat_type=ticket_type)
    flight = utils.get_flight_status_by_flight_id(flight_id=flight_id)
    user = utils.get_user_by_id(user_id=user_id)
    price = utils.get_ticket_price(flight_id=flight_id, ticket_type=ticket_type)
    aiprorts = utils.get_list_airport()
    return render_template('seat_selection.html', user_id=user_id, seats=seats, flight=flight, airports=aiprorts,
                            user=user, price=price)


@app.route('/payment')
def payment():
    err_msg = ''
    bill_id = str(uuid.uuid4())[0:6].upper()
    while utils.get_bill_by_id(bill_id=bill_id):
        bill_id = str(uuid.uuid4())[0:6].upper()
    user_id = request.args.get('user_id')
    seat_id = request.args.get('seat_id')
    employee_id = request.args.get('employee_id')
    price = utils.get_ticket_price(flight_id=flight_id, ticket_type=ticket_type)
    amount = price.price
    user = utils.get_user_by_id(user_id=user_id)
    flight = utils.get_flight_status_by_flight_id(flight_id=flight_id)
    aiprorts = utils.get_list_airport()
    seat = utils.get_seat_by_id(seat_id=seat_id)
    if employee_id == None:
        employee_id = 1
    utils.add_bill(bill_id=bill_id, employee_id=employee_id, amount=amount)
    utils.add_ticket(flight_id=flight_id, customer_id=user_id, bill_id=bill_id,
                     ticket_type=ticket_type, seat_id=seat_id)

    return render_template('payment.html', err_msg=err_msg, bill_id=bill_id, price=price, user=user, flight=flight,
                           airports=aiprorts, seat=seat)


@app.route('/flight-status')
def flight_status():
    airports = utils.get_list_airport()
    ticket_prices = utils.get_list_ticket_price()
    departure_airport = request.args.get("departure_airport")
    arrival_airport = request.args.get("arrival_airport")
    departure_day = request.args.get("departure_day")
    flight = None
    if departure_airport and arrival_airport and departure_day:
        flight = utils.get_flight_status(departure_airport=departure_airport, arrival_airport=arrival_airport,
                                         departure_day=departure_day)

    return render_template('flight_status.html', flight=flight, airports=airports)


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
            flight = utils.flight_scheduling(flight_id=flight_id, airplane_id=airplane_id, departure_airport=departure_airport,
                                             arrival_airport=arrival_airport, departure_day=departure_day,
                                             flight_time=flight_time, business_class=business_class, economy_class=economy_class,
                                             transit_airports=transit_airports, timing_points=timing_points, notes=notes)
            if flight == 1:
                err_msg = 'Thêm thành công'
            elif flight == -1:
                err_msg = 'Thêm thất bại'
            elif flight == 2:
                err_msg = 'Tuyến bay không tồn tại'
            elif flight == 3:
                err_msg = 'Mã chuyến bay đã tồn tại'
        except Exception:
            err_msg = 'Thêm thất bại'

    return render_template('flight_scheduling.html', airplanes=airplanes, airports=airports,
                           regulations=regulations, err_msg=err_msg)


@login.user_loader
def load_user(account_id):
    return utils.get_account_by_id(account_id=account_id)


if __name__ == '__main__':
    app.run(debug=True)
