from app import session
from gtfsdb.model.route import Route
from gtfsdb.model.trip import Trip


def query_routes_by_route_type(route_type):
    routes_result = session.query(Route).filter(Route.route_type == route_type).order_by(Route.route_short_name)
    routes = []
    for i in routes_result:
        for j in i.trips:
            if j.direction_id == 0:
                routes.append(
                    {'route_short_name': i.route_short_name, 'route_start_stop_name': j.start_stop.stop_name,
                     'route_end_stop_name': j.end_stop.stop_name})
                break

    return routes


def test_route_short_name(route_short_name, direction_id):
    test_trip = session.query(Trip).join(Trip.route).filter(
        Route.route_short_name == route_short_name).filter(Trip.direction_id == direction_id).first()

    return test_trip
