from app import session
from gtfsdb.model.trip import Trip
from gtfsdb.model.shape import Shape
from datetime import datetime


def test_trip(trip_id):
    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()

    return trip


def query_trip_stops(trip):
    trip_dict = {'route_short_name': trip.route.route_short_name, 'trip_start_stop_name': trip.start_stop.stop_name,
                 'trip_end_stop_name': trip.end_stop.stop_name}
    trip_stops = []
    trip_start_time = datetime.strptime(trip.start_time, '%H:%M:%S')
    for i in trip.stop_times:
        try:
            departure_time = datetime.strptime(i.departure_time, '%H:%M:%S')
        except ValueError:
            departure_time = i.departure_time.replace('24', '0', 1)
            departure_time = datetime.strptime(departure_time, "%H:%M:%S")
        seconds = (departure_time - trip_start_time).total_seconds()
        trip_stops.append({'stop_name': i.stop.stop_name,
                           'departure_time': '{0:02}:{1:02}:{2:02}'.format(departure_time.hour, departure_time.minute,
                                                                           departure_time.second),
                           'travel_time': (seconds % 3600) // 60})

    trip_dict['trip_stops'] = trip_stops

    return trip_dict


def query_trip_shapes(trip):
    shapes_result = session.query(Shape).filter(Shape.shape_id == trip.shape_id).all()
    shapes = [i.to_dict() for i in shapes_result]

    return shapes


def query_trip_stops_coordinates(trip):
    trip_stops_coordinates = []
    for i in trip.stop_times:
        if i.stop.stop_id != trip.start_stop.stop_id and i.stop.stop_id != trip.end_stop.stop_id:
            trip_stops_coordinates.append(
                {'stop_name': i.stop.stop_name, 'stop_lat': str(i.stop.stop_lat), 'stop_lon': str(i.stop.stop_lon)})

    return trip_stops_coordinates


def query_trip_terminals_coordinates(trip):
    trip_terminals_coordinates = [
        {'stop_name': trip.start_stop.stop_name, 'stop_lat': str(trip.start_stop.stop_lat),
         'stop_lon': str(trip.start_stop.stop_lon)},
        {'stop_name': trip.end_stop.stop_name, 'stop_lat': str(trip.end_stop.stop_lat),
         'stop_lon': str(trip.end_stop.stop_lon)}]

    return trip_terminals_coordinates
