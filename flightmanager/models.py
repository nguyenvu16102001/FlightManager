from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, DECIMAL
from flightmanager import db
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from datetime import datetime
from enum import Enum as Enums


class UserRole(Enums):
    CUSTOMER = 1
    EMPLOYEE = 2
    ADMIN = 3


class EmployeePosition(Enums):
    Pilot = 1
    FlightAttendant = 2
    ProcedureOfficer = 3
    AirTrafficController = 4
    MachineMaintenanceEngineer = 5
    SecurityStaff = 6
    Administrators = 7


class Account(db.Model, UserMixin):
    __tablename__ = 'account'

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    join_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole, default=UserRole.CUSTOMER))

    def __str__(self):
        return self.username

    def get_id(self):
        return self.account_id


class User(db.Model):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(10), nullable=False)
    gender = Column(String(10), nullable=False)
    date_of_birth = Column(DateTime, default=datetime.strptime("1/1/2001", "%d/%m/%Y"))
    identity_card = Column(String(15), nullable=False, unique=True)
    nationality = Column(String(50), default='Việt Nam')
    avatar = Column(String(150))
    address = Column(String(250))
    email = Column(String(50), nullable=False)
    phone = Column(String(15), nullable=False)
    notes = Column(String(200))
    accounts = relationship('Account', backref='user', lazy=True, cascade="all, delete", passive_deletes=True)
    employees = relationship('Employee', backref=backref('user', uselist=False), lazy=False, cascade="all, delete", passive_deletes=True)
    customers = relationship('Customer', backref=backref('user', uselist=False), lazy=False, cascade="all, delete", passive_deletes=True)


class Employee(db.Model):
    __tablename__ = 'employee'

    user_id = Column(Integer, ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False, primary_key=True)
    employee_position = Column(Enum(EmployeePosition, default=EmployeePosition.FlightAttendant))
    starting_date = Column(DateTime, default=datetime.now())
    salary = Column(DECIMAL(13, 3), default=0)
    bills = relationship('Bill', backref='employee', lazy=True)
    assignments = relationship('Assignment', backref='employee', lazy=True)


class Customer(db.Model):
    __tablename__ = 'customer'

    user_id = Column(Integer, ForeignKey('user.user_id', ondelete="CASCADE"), nullable=False, primary_key=True)
    mileage_acquired = Column(Integer, default=0)
    tickets = relationship('Ticket', backref='customer', lazy=True)


class Bill(db.Model):
    __tablename__ = 'bill'

    bill_id = Column(String(6), primary_key=True, nullable=False)
    employee_id = Column(Integer, ForeignKey('employee.user_id'), nullable=False)
    date_of_payment = Column(DateTime, default=datetime.now())
    amount = Column(DECIMAL(13, 3), nullable=False)
    status = Column(Boolean, default=False)
    tickets = relationship('Ticket', backref='bill', lazy=False, cascade="all, delete", passive_deletes=True)


class Airport(db.Model):
    __tablename__ = 'airport'

    airport_id = Column(String(3), nullable=False, primary_key=True)
    airport_name = Column(String(50), nullable=False, unique=True)
    location = Column(String(20), nullable=False)
    length = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    transit_airports = relationship('TransitAirport', backref='airport', lazy=True)


class Schedule(db.Model):
    __tablename__ = 'schedule'

    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    departure_airport = Column(String(3), ForeignKey('airport.airport_id'), nullable=False)
    arrival_airport = Column(String(3), ForeignKey('airport.airport_id'), nullable=False)
    departure_airports = relationship('Airport', foreign_keys=[departure_airport])
    arrival_airports = relationship('Airport', foreign_keys=[arrival_airport])
    flights = relationship('Flight', backref='schedule', lazy=True)


class TransitAirport(db.Model):
    __tablename__ = 'transit_airport'

    transit_airport_id = Column(String(3), ForeignKey('airport.airport_id'), nullable=False, primary_key=True)
    flight_id = Column(String(10), ForeignKey('flight.flight_id'), nullable=False, primary_key=True)
    timing_point = Column(Integer, default=0)
    arrival_day = Column(DateTime)
    note = Column(String(100))


class Airline(db.Model):
    __tablename__ = 'airline'

    airline_id = Column(String(2), primary_key=True)
    airline_name = Column(String(50), nullable=False, unique=True)
    address = Column(String(300), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone = Column(String(15), nullable=False, unique=True)
    airplanes = relationship('Airplane', backref='airline', lazy=True)


class Flight(db.Model):
    __tablename__ = 'flight'

    flight_id = Column(String(10), primary_key=True, nullable=False)
    airplane_id = Column(String(7), ForeignKey('airplane.airplane_id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedule.schedule_id'), nullable=False)
    flight_time = Column(Integer, default=0)
    departure_day = Column(DateTime, nullable=False)
    arrival_day = Column(DateTime, nullable=False)
    number_of_empty_seats = Column(Integer, default=0)
    seat_classes = relationship('SeatClass', backref='flight', lazy=True, cascade="all, delete", passive_deletes=True)
    ticket_prices = relationship('TicketPrice', backref='flight', lazy=True, cascade="all, delete", passive_deletes=True)
    tickets = relationship('Ticket', backref='flight', lazy=True)
    assignments = relationship('Assignment', backref='flight', lazy=True, cascade="all, delete", passive_deletes=True)
    transit_airports = relationship('TransitAirport', backref='flight', lazy=True)


class Airplane(db.Model):
    __tablename__ = 'airplane'

    airplane_id = Column(String(7), primary_key=True, nullable=False)
    airplane_type = Column(String(4), ForeignKey('airplane_type.id'), nullable=False)
    airline_id = Column(String(2), ForeignKey('airline.airline_id'), nullable=False)
    images = Column(String(200))
    active = Column(Boolean, default=True)
    seats = relationship('Seat', backref='airplane', lazy=True, cascade="all, delete", passive_deletes=True)
    flights = relationship('Flight', backref='airplane', lazy=True)


class AirplaneType(db.Model):
    __tablename__ = 'airplane_type'

    id = Column(String(4), primary_key=True, nullable=False)
    name = Column(String(50), nullable=False)
    manufacture_id = Column(Integer, ForeignKey('manufacture.manufacture_id'), nullable=False)
    length = Column(DECIMAL(4, 2), default=0)
    wingspan = Column(DECIMAL(4, 2), default=0)
    height = Column(DECIMAL(4, 2), default=0)
    seat_number = Column(Integer, default=0)
    cruising_speed = Column(Integer, default=0)
    description = Column(String(200))
    airplanes = relationship('Airplane', backref='airplane type', lazy=True)


class Manufacture(db.Model):
    __tablename__ = 'manufacture'

    manufacture_id = Column(Integer, primary_key=True, autoincrement=True)
    manufacture_name = Column(String(50), nullable=False, unique=True)
    airplane_types = relationship('AirplaneType', backref='manufacture', lazy=True)


class SeatType(db.Model):
    __tablename__ = 'seat_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    seats = relationship('Seat', backref='seat type', lazy=True)
    seat_classes = relationship('SeatClass', backref='seat type', lazy=True)


class Seat(db.Model):
    __tablename__ = 'seat'

    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    seat_name = Column(String(3), nullable=False)
    seat_type = Column(Integer, ForeignKey('seat_type.id'))
    active = Column(Boolean, default=True)
    airplane_id = Column(String(10), ForeignKey('airplane.airplane_id', ondelete="CASCADE"), nullable=False)
    tickets = relationship('Ticket', backref='seat', lazy=True)


class SeatClass(db.Model):
    __tablename__ = 'seat_class'

    flight_id = Column(String(10), ForeignKey('flight.flight_id', ondelete="CASCADE"), primary_key=True, nullable=False)
    seat_type = Column(Integer, ForeignKey('seat_type.id'), primary_key=True, nullable=False)
    seat_number = Column(Integer, default=0)


class TicketType(db.Model):
    __tablename__ = 'ticket_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False, unique=True)
    tickets = relationship('Ticket', backref='ticket type', lazy=True)
    ticket_prices = relationship('TicketPrice', backref='ticket type', lazy=True)


class TicketPrice(db.Model):
    __tablename__ = 'ticket_price'

    flight_id = Column(String(10), ForeignKey('flight.flight_id', ondelete="CASCADE"), primary_key=True, nullable=False)
    ticket_type = Column(Integer, ForeignKey('ticket_type.id'), primary_key=True)
    price = Column(DECIMAL(13, 3), default=0)
    quantity = Column(Integer, default=0)


class Ticket(db.Model):
    __tablename__ = 'ticket'

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(String(10), ForeignKey('flight.flight_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.user_id'), nullable=False)
    bill_id = Column(String(6), ForeignKey('bill.bill_id', ondelete="CASCADE"), nullable=False)
    booking_date = Column(DateTime, default=datetime.now())
    ticket_type = Column(Integer, ForeignKey('ticket_type.id'))
    seat_id = Column(Integer, ForeignKey('seat.seat_id'), nullable=False)


class Assignment(db.Model):
    __tablename__ = 'assignment'

    flight_id = Column(String(10), ForeignKey('flight.flight_id', ondelete="CASCADE"), primary_key=True, nullable=False)
    employee_id = Column(Integer, ForeignKey('employee.user_id'), primary_key=True, nullable=False)
    duty = Column(String(100), nullable=False)


class Regulations(db.Model):
    __tablename__ = 'regulations'

    regulations_id = Column(Integer, primary_key=True, autoincrement=True)
    number_of_airports = Column(Integer, default=10)
    minimum_flight_time = Column(Integer, default=30)
    maximum_number_of_intermediate_airports = Column(Integer, default=2)
    minimum_estimated_time_of_the_stop = Column(Integer, default=20)
    maximum_estimated_time_of_the_stop = Column(Integer, default=30)
    ticket_sales_time = Column(Integer, default=12)
    ticket_booking_time = Column(Integer, default=4)


if __name__ == '__main__':
    db.create_all()

    # user1 = User(last_name='Lê Đức', first_name='Hải', gender='Nam', date_of_birth=datetime.strptime("12/2/1988", "%d/%m/%Y"), identity_card='22324152', address='170/4 đường số 204 Cao Lỗ, quận 8, TP.HCM', email='leduchai1202@gmail.com', phone='9020005505')
    # user2 = User(last_name='Lê Hoàng', first_name='Sơn', gender='Nam', date_of_birth=datetime.strptime("27/03/1987", "%d/%m/%Y"), identity_card='25020255', address='615 KP2, quận Bình Tân, TP.HCM', email='lehoangson2703@gmail.com', phone='902075767')
    # user3 = User(last_name='Phan Thị Trúc', first_name='Vy', gender='Nữ', date_of_birth=datetime.strptime("26/04/1989", "%d/%m/%Y"), identity_card='24394830', address='6 Trần Huy Liệu, P.12, quận Phú Nhuận, TP.HCM', email='phanthitrucvy2604@gmail.com', phone='902076976')
    # user4 = User(last_name='Trương Thị', first_name='Minh', gender='Nữ', date_of_birth=datetime.strptime("09/06/1996", "%d/%m/%Y"), identity_card='22101378', address='19 đường 8A, quận Bình Tân, TP.HCM', email='truongthiminh0906@gmail.com', phone='902277829')
    # user5 = User(last_name='Trần Thị Ánh', first_name='Nguyệt', gender='Nữ', date_of_birth=datetime.strptime("21/10/1996", "%d/%m/%Y"), identity_card='334163212', address='265 Dương Đinh Hội, quận 9, TP.HCM', email='tranthianhnguyet@gmail.com', phone='334163212')
    # user6 = User(last_name='Lê Tuấn', first_name='Kiệt', gender='Nam', date_of_birth=datetime.strptime("24/12/1992", "%d/%m/%Y"), identity_card='24946459', address='128/4 kp3 P.Hiệp Thành, quận 12, TP.HCM', email='letuankiet@gmail.com', phone='9023110456')
    # user7 = User(last_name='Phạm Thị', first_name='Xoa', gender='Nữ', date_of_birth=datetime.strptime("09/06/1996", "%d/%m/%Y"), identity_card='151399672', address='274 Ngô Quyền P.08, quận 10, TP.HCM', email='phamthixoa@gmail.com', phone='902313123')
    # user8 = User(last_name='Nguyễn Đoàn', first_name='Quân', gender='Nam', date_of_birth=datetime.strptime("12/09/1984", "%d/%m/%Y"), identity_card='250575000', address='3-5 Lô A Khu Chung Cư Hồng Linh X.Bình Hưng, huyện Bình Chánh, TP.HCM', email='nguyendoanquan@gmail.com', phone='902329009')
    # user9 = User(last_name='Võ Thị', first_name='Thi', gender='Nữ', date_of_birth=datetime.strptime("17/07/1993", "%d/%m/%Y"), identity_card='20352687', address='52/17/2 Nguyễn Thị Thập, quận 7, TP.HCM', email='vothithi@gmail.com', phone='902373620')
    # user10 = User(last_name='Trần Anh', first_name='Tuấn', gender='Nam', date_of_birth=datetime.strptime("13/03/1989", "%d/%m/%Y"), identity_card='25053024', address='269A Tân Hương P.Tân Quý, quận Tân Phú, TP.HCM', email='trananhtuan1303@gmail.com', phone='902382328')
    # user11 = User(last_name='Hà Thị Thúy', first_name='Ngoc', gender='Nữ', date_of_birth=datetime.strptime("15/05/1995", "%d/%m/%Y"), identity_card='365701101', address='11 Phạm Thế Hiển, P.05, quận 8, TP.HCM', email='hathithuyngoc@gmail.com', phone='902404069')
    # user12 = User(last_name='Tôn Thất', first_name='Phong', gender='Nam', date_of_birth=datetime.strptime("29/01/1998", "%d/%m/%Y"), identity_card='229132231', address='35 Khu A tổ 17 P.Tân Hưng Thuân, quận 12, TP.HCM', email='tonthatphong@gmail.com', phone='902404419')
    # user13 = User(last_name='Huỳnh Chiêu', first_name='Hoàng', gender='Nam', date_of_birth=datetime.strptime("16/09/1994", "%d/%m/%Y"), identity_card='321138744', address='180B Lê Văn Sỹ, P.10, quận Phú Nhuận, TP.HCM', email='huynhchieuhoang@gmail.com', phone='902464986')
    # user14 = User(last_name='Diệp Văn', first_name='Công', gender='Nam', date_of_birth=datetime.strptime("30/11/1989", "%d/%m/%Y"), identity_card='361299165', address='140 Trần Đại Nghĩa, quận Bình Tân, TP.HCM', email='diepvancong@gmail.com', phone='902488989')
    # user15 = User(last_name='Trần Mộng', first_name='Thủy', gender='Nữ', date_of_birth=datetime.strptime("21/01/1999", "%d/%m/%Y"), identity_card='240858781', address='A2-1205 căn hộ Cantivil KP5, quận 2, TP.HCM', email='tranmongthuy@gmail.com', phone='902501690')
    # db.session.add(user1)
    # db.session.add(user2)
    # db.session.add(user3)
    # db.session.add(user4)
    # db.session.add(user5)
    # db.session.add(user6)
    # db.session.add(user7)
    # db.session.add(user8)
    # db.session.add(user9)
    # db.session.add(user10)
    # db.session.add(user11)
    # db.session.add(user12)
    # db.session.add(user13)
    # db.session.add(user14)
    # db.session.add(user15)
    # db.session.commit()
    #
    # account1 = Account(user_id=1, username='admin', password = '202cb962ac59075b964b07152d234b70', user_role = UserRole.ADMIN)
    # account2 = Account(user_id=3, username='phanthitrucvy', password='202cb962ac59075b964b07152d234b70', user_role = UserRole.EMPLOYEE)
    # account3 = Account(user_id=4, username='truongthiminh', password='202cb962ac59075b964b07152d234b70')
    # account4 = Account(user_id=5, username='tranthianhnguyet', password='202cb962ac59075b964b07152d234b70')
    # account5 = Account(user_id=7, username='phanthixoa', password='202cb962ac59075b964b07152d234b70', user_role=UserRole.EMPLOYEE)
    # account6 = Account(user_id=9, username='vothithi', password='202cb962ac59075b964b07152d234b70')
    # account7 = Account(user_id=10, username='trananhtuan', password='202cb962ac59075b964b07152d234b70')
    # account8 = Account(user_id=11, username='hathithuyngoc', password='202cb962ac59075b964b07152d234b70')
    # account9 = Account(user_id=13, username='huynhchieuhoang', password='202cb962ac59075b964b07152d234b70')
    # account10 = Account(user_id=14, username='diepvancong', password='202cb962ac59075b964b07152d234b70')
    # account11 = Account(user_id=15, username='tranmongthuy', password='202cb962ac59075b964b07152d234b70', user_role=UserRole.EMPLOYEE)
    # db.session.add(account1)
    # db.session.add(account2)
    # db.session.add(account3)
    # db.session.add(account4)
    # db.session.add(account5)
    # db.session.add(account6)
    # db.session.add(account7)
    # db.session.add(account8)
    # db.session.add(account9)
    # db.session.add(account10)
    # db.session.add(account11)
    # db.session.commit()
    #
    # employee1 = Employee(user_id='1', employee_position=EmployeePosition.Administrators, salary='15000000')
    # employee2 = Employee(user_id='2', employee_position=EmployeePosition.Pilot, salary='30000000')
    # employee3 = Employee(user_id='3', employee_position=EmployeePosition.FlightAttendant, salary='25000000')
    # employee4 = Employee(user_id='6', employee_position=EmployeePosition.MachineMaintenanceEngineer, salary='20000000')
    # employee5 = Employee(user_id='7', employee_position=EmployeePosition.ProcedureOfficer, salary='22000000')
    # employee6 = Employee(user_id='8', employee_position=EmployeePosition.Pilot, salary='30000000')
    # employee7 = Employee(user_id='12', employee_position=EmployeePosition.SecurityStaff, salary='10000000')
    # employee8 = Employee(user_id='15', employee_position=EmployeePosition.ProcedureOfficer, salary='20000000')
    # db.session.add(employee1)
    # db.session.add(employee2)
    # db.session.add(employee3)
    # db.session.add(employee4)
    # db.session.add(employee5)
    # db.session.add(employee6)
    # db.session.add(employee7)
    # db.session.add(employee8)
    # db.session.commit()
    #
    # customer1 = Customer(user_id='4')
    # customer2 = Customer(user_id='5', mileage_acquired=1000)
    # customer3 = Customer(user_id='9', mileage_acquired=9000)
    # customer4 = Customer(user_id='10', mileage_acquired=15000)
    # customer5 = Customer(user_id='11')
    # customer6 = Customer(user_id='13', mileage_acquired=8000)
    # customer7 = Customer(user_id='14')
    # db.session.add(customer1)
    # db.session.add(customer2)
    # db.session.add(customer3)
    # db.session.add(customer4)
    # db.session.add(customer5)
    # db.session.add(customer6)
    # db.session.add(customer7)
    # db.session.commit()
    #
    # airport1 = Airport(airport_id='HAN', airport_name='Sân bay Quốc tế Nội Bài', location='Hà Nội', length='3200')
    # airport2 = Airport(airport_id='HPH', airport_name='Sân bay quốc tế Cát Bi', location='Hải Phòng', length='2402')
    # # airport3 = Airport(airport_id='DIN', airport_name='Sân bay Điện Biên Phủ', location='Điện Biên', length='1830')
    # # airport4 = Airport(airport_id='THD', airport_name='Sân bay Thọ Xuân', location='Thanh Hóa', length='3200')
    # # airport5 = Airport(airport_id='VII', airport_name='Sân bay quốc tế Vinh', location='Nghệ An', length='2400')
    # # airport6 = Airport(airport_id='VDH', airport_name='Sân bay Đồng Hới', location='Quảng Bình', length='2400')
    # airport7 = Airport(airport_id='HUI', airport_name='Sân bay quốc tế Phú Bài', location='Thừa Thiên - Huế', length='2675')
    # airport8 = Airport(airport_id='DAD', airport_name='Sân bay quốc tế Đà Nẵng', location='Đà Nẵng', length='3500')
    # # airport9 = Airport(airport_id='VCL', airport_name='Sân bay quốc tế Chu Lai', location='Quảng Nam', length='3050')
    # # airport10 = Airport(airport_id='UIH', airport_name='Sân bay Phù Cát', location='Bình Định', length='3051')
    # # airport11 = Airport(airport_id='TBB', airport_name='Sân bay Tuy Hòa', location='Phú Yên', length='2902')
    # airport12 = Airport(airport_id='CXR', airport_name='Sân bay quốc tế Cam Ranh', location='Khánh Hòa', length='3048')
    # airport13 = Airport(airport_id='BMV', airport_name='Sân bay Buôn Ma Thuột', location='Đắk Lắk', length='3000')
    # airport14 = Airport(airport_id='DLI', airport_name='Sân bay Liên Khương', location='Lâm Đồng', length='3250')
    # airport15 = Airport(airport_id='PXU', airport_name='Sân bay Pleiku', location='Gia Lai', length='1817')
    # airport16 = Airport(airport_id='SGN', airport_name='Sân bay quốc tế Tân Sơn Nhất', location='TP HCM', length='3048')
    # # airport17 = Airport(airport_id='CAH', airport_name='Sân bay Cà Mau', location='Cà Mau', length='1500')
    # # airport18 = Airport(airport_id='VCS', airport_name='Sân bay Côn Đảo', location='Bà Rịa-Vũng Tàu', length='1287')
    # # airport19 = Airport(airport_id='VCA', airport_name='Sân bay quốc tế Cần Thơ', location='Cần Thơ', length='3000')
    # # airport20 = Airport(airport_id='VKG', airport_name='Sân bay Rạch Giá', location='Kiên Giang', length='1500')
    # # airport21 = Airport(airport_id='PQC', airport_name='Sân bay quốc tế Phú Quốc', location='Kiên Giang', length='3000')
    # # airport22 = Airport(airport_id='CDO', airport_name='Sân bay Quốc tế Vân Đồn', location='Quảng Ninh', length='3600')
    # db.session.add(airport1)
    # db.session.add(airport2)
    # db.session.add(airport7)
    # db.session.add(airport8)
    # db.session.add(airport12)
    # db.session.add(airport13)
    # db.session.add(airport14)
    # db.session.add(airport15)
    # db.session.add(airport16)
    # # db.session.add(airport21)
    # # db.session.add(airport22)
    # db.session.commit()
    #
    # airline1 = Airline(airline_id='VN', airline_name='Vietnam Airline', address='Số 200 Nguyễn Sơn, P.Bồ Đề, Q.Long Biên, Hà Nội', email='Telesales@vietnamairlines.com', phone='(84) 38272289')
    # airline2 = Airline(airline_id='VJ', airline_name='Vietjet Air', address='302/3 Phố Kim Mã, Phường Ngọc Khánh, Quận Ba Đình, TP. Hà Nội, Việt Nam', email='19001886@vietjetair.com', phone='(028) 3830 6755')
    # airline3 = Airline(airline_id='BL', airline_name='Jetstar Pacific Airlines', address='Tầng 3, Tòa nhà điều hành Tổng công ty Hàng không Việt Nam, Sân bay quốc tế Tân Sơn Nhất. Tân Bình, TP. Hồ Chí Minh, Việt Nam', email='www.pacificairlines.com.vn', phone='8428. 36280058')
    # airline4 = Airline(airline_id='QH', airline_name='Bamboo Airways', address='Tầng 22, Tòa nhà Bamboo Airways Tower, 265 Cầu Giấy, Phường Dịch Vọng, Quận Cầu Giấy, Hà Nội', email='info@bambooairways.com', phone='02432333233')
    # db.session.add(airline1)
    # db.session.add(airline2)
    # db.session.add(airline3)
    # db.session.add(airline4)
    # db.session.commit()
    #
    # manufacture1 = Manufacture(manufacture_name='Airbus')
    # manufacture2 = Manufacture(manufacture_name='Boeing')
    # manufacture3 = Manufacture(manufacture_name='Embraer')
    # db.session.add(manufacture1)
    # db.session.add(manufacture2)
    # db.session.add(manufacture3)
    # db.session.commit()
    #
    # airplanetype1 = AirplaneType(id='B78X', name='Boeing 787-10 Dreamliner', manufacture_id='2', length='63.73', wingspan='60.93', height='18.76', seat_number='274', cruising_speed='954')
    # airplanetype2 = AirplaneType(id='A359', name='Airbus A350-941', manufacture_id='1', length='66.89', wingspan='64.75', height='17.05', seat_number='305', cruising_speed='901')
    # airplanetype3 = AirplaneType(id='A321', name='Airbus A321-231', manufacture_id='1', length='44.51', wingspan='34.1', height='11.76', seat_number='184', cruising_speed='950')
    # airplanetype4 = AirplaneType(id='B737', name='Boeing 737 MAX 200', manufacture_id='2', length='39.5', wingspan='35.92', height='11.76', seat_number='162', cruising_speed='839')
    # airplanetype5 = AirplaneType(id='A320', name='Airbus A320-232', manufacture_id='1', length='37.57', wingspan='34.1', height='11.76', seat_number='180', cruising_speed='950')
    # airplanetype6 = AirplaneType(id='B787', name='Boeing 787-8 Dreamliner', manufacture_id='2', length='56.72', wingspan='60.12', height='17.02', seat_number='359', cruising_speed='945')
    # airplanetype7 = AirplaneType(id='A21N', name='Airbus A321neo', manufacture_id='1', length='44.51', wingspan='35.8', height='11.76', seat_number='232', cruising_speed='876')
    # airplanetype8 = AirplaneType(id='A20N', name='Airbus A320neo', manufacture_id='1', length='37.57', wingspan='35.8', height='11.76', seat_number='170', cruising_speed='820')
    # airplanetype9 = AirplaneType(id='E190', name='Embraer E190LR', manufacture_id='3', length='36.24', wingspan='28.72', height='10.28', seat_number='116', cruising_speed='871')
    # db.session.add(airplanetype1)
    # db.session.add(airplanetype2)
    # db.session.add(airplanetype3)
    # db.session.add(airplanetype4)
    # db.session.add(airplanetype5)
    # db.session.add(airplanetype6)
    # db.session.add(airplanetype7)
    # db.session.add(airplanetype8)
    # db.session.add(airplanetype9)
    # db.session.commit()
    #
    # airplane1 = Airplane(airplane_id='VN-A323', airplane_type='A321', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640422815/AirplaneType/79365_1636774692_zibtgw.webp')
    # airplane2 = Airplane(airplane_id='VN-A501', airplane_type='A21N', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640422349/AirplaneType/59829_1638371830_uyufyk.webp')
    # airplane3 = Airplane(airplane_id='VN-A503', airplane_type='A21N', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640422349/AirplaneType/59829_1638371830_uyufyk.webp')
    # airplane4 = Airplane(airplane_id='VN-A886', airplane_type='A359', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640422565/AirplaneType/36345_1638665114_sgktdz.jpg')
    # airplane5 = Airplane(airplane_id='VN-A326', airplane_type='A321', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640422815/AirplaneType/79365_1636774692_zibtgw.webp')
    # airplane6 = Airplane(airplane_id='VN-A872', airplane_type='B78X', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640440470/AirplaneType/55944_1638369877_yvwyjc.webp')
    # airplane7 = Airplane(airplane_id='VN-A878', airplane_type='B78X', airline_id='VN', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640440470/AirplaneType/55944_1638369877_yvwyjc.webp')
    # airplane8 = Airplane(airplane_id='VN-A521', airplane_type='A21N', airline_id='VJ', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640440729/AirplaneType/80996_1639235606_zvg5mh.webp')
    # airplane9 = Airplane(airplane_id='VN-A672', airplane_type='A320', airline_id='VJ', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640440964/AirplaneType/31098_1607592956_huwoc6.webp')
    # airplane10 = Airplane(airplane_id='VN-A522', airplane_type='A321', airline_id='VJ', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640441197/AirplaneType/56320_1606148018_bjtz0m.webp')
    # airplane11 = Airplane(airplane_id='VN-A535', airplane_type='A321', airline_id='VJ', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640441197/AirplaneType/56320_1606148018_bjtz0m.webp')
    # airplane12 = Airplane(airplane_id='VN-A198', airplane_type='A320', airline_id='BL', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640441876/AirplaneType/71186_1639244657_cbcumj.webp')
    # airplane13 = Airplane(airplane_id='VN-A565', airplane_type='B787', airline_id='BL', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442031/AirplaneType/download_q6iqsq.jpg')
    # airplane14 = Airplane(airplane_id='VN-A566', airplane_type='B787', airline_id='BL', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442031/AirplaneType/download_q6iqsq.jpg')
    # airplane15 = Airplane(airplane_id='VN-A571', airplane_type='A21N', airline_id='BL', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442236/AirplaneType/download_choqxu.jpg')
    # airplane16 = Airplane(airplane_id='VN-A577', airplane_type='A321', airline_id='BL', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442431/AirplaneType/images_d8lzfr.jpg')
    # airplane17 = Airplane(airplane_id='VN-A226', airplane_type='A20N', airline_id='QH', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442607/AirplaneType/44208_1638721085_uf8g23.webp')
    # airplane18 = Airplane(airplane_id='VN-A222', airplane_type='A21N', airline_id='QH', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442806/AirplaneType/24831_1639030976_nnm0ib.webp')
    # airplane19 = Airplane(airplane_id='VN-A582', airplane_type='A320', airline_id='QH', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640442897/AirplaneType/29750_1613392072_nmauxr.jpg')
    # airplane20 = Airplane(airplane_id='VN-A585', airplane_type='A321', airline_id='QH', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640443030/AirplaneType/38417_1635233053_eixq81.webp')
    # airplane21 = Airplane(airplane_id='VN-A818', airplane_type='B78X', airline_id='QH', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640443115/AirplaneType/29694_1638373409_w59b7n.webp')
    # airplane22 = Airplane(airplane_id='VN-A262', airplane_type='E190', airline_id='QH', images='https://res.cloudinary.com/dufpogfsu/image/upload/v1640443173/AirplaneType/80672_1635868684_jf4lat.webp')
    # db.session.add(airplane1)
    # db.session.add(airplane2)
    # db.session.add(airplane3)
    # db.session.add(airplane4)
    # db.session.add(airplane5)
    # db.session.add(airplane6)
    # db.session.add(airplane7)
    # db.session.add(airplane8)
    # db.session.add(airplane9)
    # db.session.add(airplane10)
    # db.session.add(airplane11)
    # db.session.add(airplane12)
    # db.session.add(airplane13)
    # db.session.add(airplane14)
    # db.session.add(airplane15)
    # db.session.add(airplane16)
    # db.session.add(airplane17)
    # db.session.add(airplane18)
    # db.session.add(airplane19)
    # db.session.add(airplane20)
    # db.session.add(airplane21)
    # db.session.add(airplane22)
    # db.session.commit()
    #
    # schedule1 = Schedule(departure_airport='HAN', arrival_airport='DAD')
    # schedule2 = Schedule(departure_airport='HAN', arrival_airport='SGN')
    # schedule3 = Schedule(departure_airport='HAN', arrival_airport='CXR')
    # schedule4 = Schedule(departure_airport='HAN', arrival_airport='DLI')
    # schedule5 = Schedule(departure_airport='SGN', arrival_airport='HAN')
    # schedule6 = Schedule(departure_airport='SGN', arrival_airport='CXR')
    # schedule7 = Schedule(departure_airport='SGN', arrival_airport='DLI')
    # schedule8 = Schedule(departure_airport='SGN', arrival_airport='DAD')
    # schedule9 = Schedule(departure_airport='DAD', arrival_airport='HAN')
    # schedule10 = Schedule(departure_airport='DAD', arrival_airport='SGN')
    # schedule11 = Schedule(departure_airport='DAD', arrival_airport='CXR')
    # schedule12 = Schedule(departure_airport='DAD', arrival_airport='DLI')
    # schedule13 = Schedule(departure_airport='CXR', arrival_airport='HAN')
    # schedule14 = Schedule(departure_airport='CXR', arrival_airport='SGN')
    # schedule15 = Schedule(departure_airport='CXR', arrival_airport='DAD')
    # schedule16 = Schedule(departure_airport='DLI', arrival_airport='HAN')
    # schedule17 = Schedule(departure_airport='DLI', arrival_airport='SGN')
    # schedule18 = Schedule(departure_airport='DLI', arrival_airport='DAD')
    # db.session.add(schedule1)
    # db.session.add(schedule2)
    # db.session.add(schedule3)
    # db.session.add(schedule4)
    # db.session.add(schedule5)
    # db.session.add(schedule6)
    # db.session.add(schedule7)
    # db.session.add(schedule8)
    # db.session.add(schedule9)
    # db.session.add(schedule10)
    # db.session.add(schedule11)
    # db.session.add(schedule12)
    # db.session.add(schedule13)
    # db.session.add(schedule14)
    # db.session.add(schedule15)
    # db.session.add(schedule16)
    # db.session.add(schedule17)
    # db.session.add(schedule18)
    # db.session.commit()
    #
    # flight1 = Flight(flight_id='VN 116', airplane_id='VN-A323', schedule_id='5', flight_time='85', departure_day=datetime.strptime("28/12/2021 09:10:00", "%d/%m/%Y %H:%M:%S"), arrival_day=datetime.strptime("28/12/2021 16:40:00", "%d/%m/%Y %H:%M:%S"), number_of_empty_seats='50')
    # flight2 = Flight(flight_id='VN 6078', airplane_id='VN-A198', schedule_id='9', flight_time='80', departure_day=datetime.strptime("28/12/2021 15:20:00", "%d/%m/%Y %H:%M:%S"), arrival_day=datetime.strptime("28/12/2021 16:40:00", "%d/%m/%Y %H:%M:%S"), number_of_empty_seats='30')
    # flight3 = Flight(flight_id='VN 1954', airplane_id='VN-A323', schedule_id='18', flight_time='90', departure_day=datetime.strptime("30/12/2021 11:10:00", "%d/%m/%Y %H:%M:%S"), arrival_day=datetime.strptime("30/12/2021 12:40:00", "%d/%m/%Y %H:%M:%S"), number_of_empty_seats='20')
    # flight4 = Flight(flight_id='VJ601', airplane_id='VN-A535', schedule_id='14', flight_time='65', departure_day=datetime.strptime("29/12/2021 10:45:00", "%d/%m/%Y %H:%M:%S"), arrival_day=datetime.strptime("29/12/2021 11:50:00", "%d/%m/%Y %H:%M:%S"), number_of_empty_seats='25')
    # db.session.add(flight1)
    # db.session.add(flight2)
    # db.session.add(flight3)
    # db.session.add(flight4)
    # db.session.commit()
    #
    # transitairport1 = TransitAirport(transit_airport_id='DAD', flight_id='VN 116', timing_point='25', arrival_day=datetime.strptime("28/12/2021 10:35:00", "%d/%m/%Y %H:%M:%S"))
    # db.session.add(transitairport1)
    # db.session.commit()
    #
    # seat_type1 = SeatType(name='BusinessClass')
    # seat_type2 = SeatType(name='EconomyClass')
    # db.session.add(seat_type1)
    # db.session.add(seat_type2)
    # db.session.commit()
    #
    # ticket_type1 = TicketType(name='BusinessClass')
    # ticket_type2 = TicketType(name='EconomyClass')
    # db.session.add(ticket_type1)
    # db.session.add(ticket_type2)
    # db.session.commit()
    #
    # ticket_price1 = TicketPrice(flight_id='VN 1954', ticket_type=2, price='1550000', quantity=130)
    # ticket_price2 = TicketPrice(flight_id='VN 1954', ticket_type=1, price='4431000', quantity=54)
    # ticket_price3 = TicketPrice(flight_id='VN 116', ticket_type=2, price='1575000', quantity=130)
    # ticket_price4 = TicketPrice(flight_id='VN 116', ticket_type=1, price='4100000', quantity=54)
    # ticket_price5 = TicketPrice(flight_id='VN 6078', ticket_type=2, price='1700000', quantity=140)
    # ticket_price6 = TicketPrice(flight_id='VN 6078', ticket_type=1, price='4650000', quantity=40)
    # ticket_price7 = TicketPrice(flight_id='VJ601', ticket_type=2, price='1450000', quantity=144)
    # ticket_price8 = TicketPrice(flight_id='VJ601', ticket_type=1, price='4500000', quantity=40)
    # db.session.add(ticket_price1)
    # db.session.add(ticket_price2)
    # db.session.add(ticket_price3)
    # db.session.add(ticket_price4)
    # db.session.add(ticket_price5)
    # db.session.add(ticket_price6)
    # db.session.add(ticket_price7)
    # db.session.add(ticket_price8)
    # db.session.commit()
    #
    # seat_class1 = SeatClass(flight_id='VN 1954', seat_type=2, seat_number=130)
    # seat_class2 = SeatClass(flight_id='VN 1954', seat_type=1, seat_number=54)
    # seat_class3 = SeatClass(flight_id='VN 116', seat_type=2, seat_number=130)
    # seat_class4 = SeatClass(flight_id='VN 116', seat_type=1, seat_number=54)
    # seat_class5 = SeatClass(flight_id='VN 6078', seat_type=2, seat_number=140)
    # seat_class6 = SeatClass(flight_id='VN 6078', seat_type=1, seat_number=40)
    # seat_class7 = SeatClass(flight_id='VJ601', seat_type=2, seat_number=144)
    # seat_class8 = SeatClass(flight_id='VJ601', seat_type=1, seat_number=40)
    # db.session.add(seat_class1)
    # db.session.add(seat_class2)
    # db.session.add(seat_class3)
    # db.session.add(seat_class4)
    # db.session.add(seat_class5)
    # db.session.add(seat_class6)
    # db.session.add(seat_class7)
    # db.session.add(seat_class8)
    # db.session.commit()
    #
    # assignment1 = Assignment(flight_id='VN 116', employee_id='2', duty='captain')
    # assignment2 = Assignment(flight_id='VN 116', employee_id='8', duty='first officer')
    # assignment3 = Assignment(flight_id='VN 116', employee_id='3', duty='flight attendant')
    # assignment4 = Assignment(flight_id='VN 6078', employee_id='2', duty='first officer')
    # assignment5 = Assignment(flight_id='VN 6078', employee_id='8', duty='captain')
    # assignment6 = Assignment(flight_id='VN 6078', employee_id='3', duty='flight attendant')
    # assignment7 = Assignment(flight_id='VN 1954', employee_id='2', duty='first officer')
    # assignment8 = Assignment(flight_id='VN 1954', employee_id='8', duty='captain')
    # assignment9 = Assignment(flight_id='VN 1954', employee_id='3', duty='flight attendant')
    # assignment10 = Assignment(flight_id='VJ601', employee_id='2', duty='first officer')
    # assignment11 = Assignment(flight_id='VJ601', employee_id='8', duty='captain')
    # assignment12 = Assignment(flight_id='VJ601', employee_id='3', duty='flight attendant')
    # db.session.add(assignment1)
    # db.session.add(assignment2)
    # db.session.add(assignment3)
    # db.session.add(assignment4)
    # db.session.add(assignment5)
    # db.session.add(assignment6)
    # db.session.add(assignment7)
    # db.session.add(assignment8)
    # db.session.add(assignment9)
    # db.session.add(assignment10)
    # db.session.add(assignment11)
    # db.session.add(assignment12)
    # db.session.commit()
    #
    # bill1 = Bill(bill_id='89AD54' ,employee_id='7', amount=3150000, status=True)
    # bill2 = Bill(bill_id='9A4EB6' ,employee_id='7', amount=4100000, status=True)
    # db.session.add(bill1)
    # db.session.add(bill2)
    # db.session.commit()
    #
    # ticket1 = Ticket(flight_id='VN 116', customer_id='4', bill_id='89AD54', ticket_type='2', seat_id='55')
    # ticket2 = Ticket(flight_id='VN 116', customer_id='4', bill_id='89AD54', ticket_type='2', seat_id='56')
    # ticket3 = Ticket(flight_id='VN 116', customer_id='9', bill_id='9A4EB6', ticket_type='1', seat_id='9')
    # db.session.add(ticket1)
    # db.session.add(ticket2)
    # db.session.add(ticket3)
    # db.session.commit()
    #
    # regulations = Regulations()
    # db.session.add(regulations)
    # db.session.commit()

