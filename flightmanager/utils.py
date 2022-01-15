from datetime import datetime, timedelta
from flightmanager import app, db
from flightmanager.models import *
from sqlalchemy.sql import extract
import hashlib


def get_account_by_id(account_id):
    return Account.query.get(account_id)


def check_login(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()


def get_user(identity_card):
    user = User.query.filter(User.identity_card.__eq__(identity_card)).first()

    return user


def add_user(last_name, first_name, gender, date_of_birth, identity_card, nationality, avatar, address, phone, email):
    user = User(last_name=last_name,
                first_name=first_name,
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


def register_customer(last_name, first_name, gender, date_of_birth, identity_card, nationality, avatar, address, phone, email, username, password):
    add_user(last_name=last_name, first_name=first_name, gender=gender, date_of_birth=date_of_birth,
             identity_card=identity_card, nationality=nationality, avatar=avatar,
             address=address, phone=phone, email=email)

    user = get_user(identity_card=identity_card)

    add_customer(user_id=user.user_id)

    add_acccount(user_id=user.user_id, username=username, password=password)


def get_list_airplane():
    return Airplane.query.filter(Airplane.active.__eq__(True)).all()


def get_list_airport():
    return Airport.query.filter(Airport.active.__eq__(True)).all()


def get_regulations_by_id(regulations_id):
    return Regulations.query.get(regulations_id)


def get_schedule_id(departure_airport, arrival_airport):
    return db.session.query(Schedule.schedule_id)\
            .filter(Schedule.departure_airport.__eq__(departure_airport), Schedule.arrival_airport.__eq__(arrival_airport)).first()


def add_flight(flight_id, airplane_id, schedule_id, flight_time, departure_day, arrival_day, number_of_empty_seats):
    flight = Flight(flight_id=flight_id, airplane_id=airplane_id, schedule_id=schedule_id,
                    flight_time=flight_time, departure_day=departure_day,
                    arrival_day=arrival_day, number_of_empty_seats=number_of_empty_seats)
    db.session.add(flight)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def delete_flight(flight):
    db.session.delete(flight)
    db.session.commit()


def add_seat_class(flight_id, business_class, economy_class):
    seat_class1 = SeatClass(flight_id=flight_id, seat_type=1, seat_number=business_class)
    seat_class2 = SeatClass(flight_id=flight_id, seat_type=2, seat_number=economy_class)

    db.session.add(seat_class1)
    db.session.add(seat_class2)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def add_transit_airport(transit_airport_id, flight_id, timing_point, arrival_day=None, note=None):
    transit_airport = TransitAirport(transit_airport_id=transit_airport_id, flight_id=flight_id,
                                     timing_point=timing_point, arrival_day=arrival_day, note=note)
    db.session.add(transit_airport)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def delete_transit_airport(flight_id):
    transit = TransitAirport.query.filter(TransitAirport.flight_id.__eq__(flight_id)).all()
    if transit:
        db.session.delete(transit)
        db.session.commit()


def flight_scheduling(flight_id, airplane_id, departure_airport, arrival_airport, departure_day, flight_time, business_class, economy_class, transit_airports, timing_points, notes):
    schedule = get_schedule_id(departure_airport=departure_airport, arrival_airport=arrival_airport)
    if get_flight_by_id(flight_id=flight_id):
        return 3
    else:
        if schedule:
            try:
                add_flight(flight_id=flight_id, airplane_id=airplane_id, schedule_id=schedule.schedule_id,
                           flight_time=flight_time, departure_day=departure_day,
                           arrival_day=datetime.strptime(departure_day, "%Y-%m-%dT%H:%M") + timedelta(minutes=int(flight_time)),
                           number_of_empty_seats=int(business_class) + int(economy_class))

                add_seat_class(flight_id=flight_id, business_class=business_class, economy_class=economy_class)

                for i in range(len(transit_airports)):
                    if transit_airports:
                        add_transit_airport(transit_airport_id=transit_airports[i], flight_id=flight_id,
                                            timing_point=timing_points[i], arrival_day=departure_day, note=notes[i])
                return 1
            except:
                flight = get_flight_by_id(flight_id=flight_id)
                if flight:
                    delete_transit_airport(flight_id=flight_id)
                    delete_flight(flight=flight)
        else:
            return 2
    return -1


def get_flight_by_id(flight_id):
    return Flight.query.get(flight_id)


def get_flight_status(departure_airport, arrival_airport, departure_day):
    departure_day = datetime.strptime(departure_day, "%Y-%m-%d")
    status = db.session.query(Flight.flight_id, Flight.airplane_id, Flight.flight_time, Flight.departure_day,
                              Flight.arrival_day, AirplaneType.name, Airline.airline_name,
                              Schedule.departure_airport, Schedule.arrival_airport) \
        .join(Airplane, Airplane.airplane_id.__eq__(Flight.airplane_id)) \
        .join(Airline, Airline.airline_id.__eq__(Airplane.airline_id)) \
        .join(AirplaneType, AirplaneType.id.__eq__(Airplane.airplane_type)) \
        .join(Schedule, Schedule.schedule_id.__eq__(Flight.schedule_id))

    if departure_airport and arrival_airport and departure_day:
        status = status.filter(Schedule.departure_airport.__eq__(departure_airport),
                               Schedule.arrival_airport.__eq__(arrival_airport),
                               extract('day', Flight.departure_day) == departure_day.day,
                               extract('month', Flight.departure_day) == departure_day.month,
                               extract('year', Flight.departure_day) == departure_day.year)
    return status.all()


def get_flight_status_by_flight_id(flight_id):
    status = db.session.query(Flight.flight_id, Flight.airplane_id, Flight.flight_time, Flight.departure_day,
                              Flight.arrival_day, AirplaneType.name, Airline.airline_name,
                              Schedule.departure_airport, Schedule.arrival_airport) \
        .join(Airplane, Airplane.airplane_id.__eq__(Flight.airplane_id)) \
        .join(Airline, Airline.airline_id.__eq__(Airplane.airline_id)) \
        .join(AirplaneType, AirplaneType.id.__eq__(Airplane.airplane_type)) \
        .join(Schedule, Schedule.schedule_id.__eq__(Flight.schedule_id))
    status = status.filter(Flight.flight_id.__eq__(flight_id))

    return status.first()


def get_seats(flight_id, seat_type):
    flight = get_flight_by_id(flight_id=flight_id)
    seats = db.session.query(Seat.seat_id, Seat.seat_name, Seat.active)\
                      .filter(Seat.airplane_id.__eq__(flight.airplane_id),
                              Seat.seat_type.__eq__(seat_type))

    return seats.all()


def get_list_ticket_price():
    return TicketPrice.query.all()


def get_ticket_price(flight_id, ticket_type):
    return TicketPrice.query.filter(TicketPrice.flight_id.__eq__(flight_id), TicketPrice.ticket_type.__eq__(ticket_type)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_bill_by_id(bill_id):
    return Bill.query.get(bill_id)


def add_ticket(flight_id, customer_id, bill_id, ticket_type, seat_id):
    ticket = Ticket(flight_id=flight_id, customer_id=customer_id, bill_id=bill_id,
                    ticket_type=ticket_type, seat_id=seat_id)

    db.session.add(ticket)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def add_bill(bill_id, employee_id, amount):
    bill = Bill(bill_id=bill_id, employee_id=employee_id, amount=amount)

    db.session.add(bill)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise


def get_seat_by_id(seat_id):
    return Seat.query.get(seat_id)