from app import session, cache
from gtfsdb.model.stop import Stop
from gtfsdb.model.route import Route
from gtfsdb.model.trip import Trip
from datetime import datetime


@cache.cached(timeout=86400, key_prefix='graph')
def generate_graph():
    stops_name_result = session.query(Stop.stop_name).group_by(Stop.stop_name).all()
    graph = {}
    for i in stops_name_result:
        graph[i[0]] = []

    route_name_result = session.query(Route.route_short_name).group_by(Route.route_short_name).all()
    for i in route_name_result:
        direction_0 = session.query(Trip).join(Trip.route).filter(
            Route.route_short_name == i[0]).filter(Trip.direction_id == 0).first()
        direction_1 = session.query(Trip).join(Trip.route).filter(
            Route.route_short_name == i[0]).filter(Trip.direction_id == 1).first()
        for j in (direction_0, direction_1):
            if j is not None:
                stops_length = len(j.stop_times)
                for index, stop_time in enumerate(j.stop_times):
                    if index < stops_length - 1:
                        try:
                            current_departure_time = datetime.strptime(stop_time.departure_time, '%H:%M:%S')
                        except ValueError:
                            current_departure_time = stop_time.departure_time.replace('24', '0', 1)
                            current_departure_time = datetime.strptime(current_departure_time, "%H:%M:%S")

                        try:
                            next_departure_time = datetime.strptime(j.stop_times[index + 1].departure_time, '%H:%M:%S')
                        except ValueError:
                            next_departure_time = j.stop_times[index + 1].departure_time.replace('24', '0', 1)
                            next_departure_time = datetime.strptime(next_departure_time, "%H:%M:%S")

                        graph[stop_time.stop.stop_name].append({'name': j.stop_times[index + 1].stop.stop_name, 'cost':(
                            next_departure_time - current_departure_time).total_seconds(), 'route': j.route.route_short_name})

    return graph
