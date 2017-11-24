from app import session
from gtfsdb.model.calendar import UniversalCalendar
from gtfsdb.model.trip import Trip
from gtfsdb.model.route import Route
from datetime import datetime


def query_dates():
    dates_result = session.query(UniversalCalendar.date).distinct().order_by(UniversalCalendar.date)
    dates = [str(date[0]) for date in dates_result]

    return dates


def query_trips_schedule(route_short_name, direction_id, date, trip):
    trips = session.query(Trip).join(Trip.route).join(UniversalCalendar,
                                                      Trip.service_id == UniversalCalendar.service_id).filter(
        Route.route_short_name == route_short_name).filter(Trip.direction_id == direction_id).filter(
        UniversalCalendar.date == date).all()

    trips_dict = {'route_short_name': trip.route.route_short_name,
                  'trip_start_stop_name': trip.start_stop.stop_name,
                  'trip_end_stop_name': trip.end_stop.stop_name,
                  'date': date}

    return trips, trips_dict


def generate_schedule_dictionary(trips, trips_dict):
    hours = [x for x in range(24)]
    hours_dict = {el: [] for el in hours}

    for i in trips:
        start_time = datetime.strptime(i.start_time, '%H:%M:%S')
        hours_dict[start_time.hour].append(
            {'trip_id': i.trip_id, 'trip_start_time': '{0:02}'.format(start_time.minute)})

    trips_dict['hours'] = hours_dict

    return trips_dict
