from flask import send_file, Response, request, url_for, redirect

from gtfsdb.model.route import Route
from gtfsdb.model.trip import Trip
from gtfsdb.model.shape import Shape
from gtfsdb.model.calendar import UniversalCalendar
from gtfsdb.model.stop import Stop

from datetime import datetime
from app import app, session

from menetrend.graph import generate_graph
from menetrend.trip_planner import dijkstra

import logging
import json

log = logging.getLogger(__name__)


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@app.route('/')
def index():
    return send_file('templates/index.html')


@app.route('/get_bus_routes', methods=['GET'])
def get_bus_routes():
    bus_routes_result = session.query(Route).filter(Route.route_type == 3).order_by(Route.route_short_name)
    bus_routes = []
    for i in bus_routes_result:
        for j in i.trips:
            if j.direction_id == 0:
                bus_routes.append(
                    {'route_short_name': i.route_short_name, 'route_start_stop_name': j.start_stop.stop_name,
                     'route_end_stop_name': j.end_stop.stop_name})
                break

    response = Response(response=json.dumps(bus_routes), status=200, mimetype='application/json')
    return response


@app.route('/get_tram_routes', methods=['GET'])
def get_tram_routes():
    tram_routes_result = session.query(Route).filter(Route.route_type == 0).order_by(Route.route_short_name)
    tram_routes = []
    for i in tram_routes_result:
        for j in i.trips:
            if j.direction_id == 0:
                tram_routes.append(
                    {'route_short_name': i.route_short_name, 'route_start_stop_name': j.start_stop.stop_name,
                     'route_end_stop_name': j.end_stop.stop_name})
                break

    response = Response(response=json.dumps(tram_routes), status=200, mimetype='application/json')
    return response


@app.route('/get_start_times', methods=['GET'])
def get_start_times():
    route_short_name = request.args.get('route_short_name')
    direction_id = request.args.get('direction_id')
    date = request.args.get('date')

    if int(direction_id) not in [0, 1]:
        response = Response(status=404)
        return response

    test_route_short_name = session.query(Trip).join(Trip.route).filter(
        Route.route_short_name == route_short_name).filter(Trip.direction_id == direction_id).first()

    if test_route_short_name is None:
        response = Response(status=404)
        return response

    trips = session.query(Trip).join(Trip.route).join(UniversalCalendar,
                                                      Trip.service_id == UniversalCalendar.service_id).filter(
        Route.route_short_name == route_short_name).filter(Trip.direction_id == direction_id).filter(
        UniversalCalendar.date == date).all()

    trips_dict = {'route_short_name': test_route_short_name.route.route_short_name,
                  'trip_start_stop_name': test_route_short_name.start_stop.stop_name,
                  'trip_end_stop_name': test_route_short_name.end_stop.stop_name,
                  'date': date}

    if not trips:
        response = Response(response=json.dumps(trips_dict), status=400)
        return response

    hours = [x for x in range(24)]
    hours_dict = {el: [] for el in hours}

    for i in trips:
        start_time = datetime.strptime(i.start_time, '%H:%M:%S')
        hours_dict[start_time.hour].append(
            {'trip_id': i.trip_id, 'trip_start_time': '{0:02}'.format(start_time.minute)})

    trips_dict['hours'] = hours_dict

    response = Response(response=json.dumps(trips_dict), status=200, mimetype='application/json')
    return response


@app.route('/get_dates', methods=['GET'])
def get_dates():
    dates_result = session.query(UniversalCalendar.date).distinct().order_by(UniversalCalendar.date)
    dates = [str(date[0]) for date in dates_result]
    response = Response(response=json.dumps(dates), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_stops', methods=['GET'])
def get_trip_stops():
    trip_id = request.args.get('trip_id')

    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()

    if trip is None:
        response = Response(status=400)
        return response

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

    response = Response(response=json.dumps(trip_dict), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_shapes', methods=['GET'])
def get_trip_shapes():
    trip_id = request.args.get('trip_id')

    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()

    if trip is None:
        response = Response(status=400)
        return response

    shapes_result = session.query(Shape).filter(Shape.shape_id == trip.shape_id).all()
    shapes = [i.to_dict() for i in shapes_result]

    response = Response(response=json.dumps(shapes), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_stops_coordinates', methods=['GET'])
def get_trip_stops_coordinates():
    trip_id = request.args.get('trip_id')

    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()

    if trip is None:
        response = Response(status=400)
        return response

    trip_stops_coordinates = []
    for i in trip.stop_times:
        if i.stop.stop_id != trip.start_stop.stop_id and i.stop.stop_id != trip.end_stop.stop_id:
            trip_stops_coordinates.append(
                {'stop_name': i.stop.stop_name, 'stop_lat': str(i.stop.stop_lat), 'stop_lon': str(i.stop.stop_lon)})

    response = Response(response=json.dumps(trip_stops_coordinates), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_terminals_coordinates', methods=['GET'])
def get_trip_terminals_coordinates():
    trip_id = request.args.get('trip_id')

    trip = session.query(Trip).filter(Trip.trip_id == trip_id).first()

    if trip is None:
        response = Response(status=400)
        return response

    trip_terminals_coordinates = [
        {'stop_name': trip.start_stop.stop_name, 'stop_lat': str(trip.start_stop.stop_lat),
         'stop_lon': str(trip.start_stop.stop_lon)},
        {'stop_name': trip.end_stop.stop_name, 'stop_lat': str(trip.end_stop.stop_lat),
         'stop_lon': str(trip.end_stop.stop_lon)}]

    response = Response(response=json.dumps(trip_terminals_coordinates), status=200, mimetype='application/json')
    return response


@app.route('/get_all_stops', methods=['GET'])
def get_all_stops():
    stops_result = session.query(Stop).group_by(Stop.stop_name).all()
    stops = [i.to_dict() for i in stops_result]

    response = Response(response=json.dumps(stops), status=200, mimetype='application/json')
    return response


@app.route('/plan_trip', methods=['POST'])
def plan_trip():
    request_data = request.json
    graph = generate_graph()
    log.debug(request_data['from'])
    path, cost = dijkstra(graph, {'name': request_data['from'], 'route': None}, request_data['to'], visited=[],
                          distances={}, predecessors={})
    response = Response(response=json.dumps(path), status=200, mimetype='application/json')
    return response


if __name__ == '__main__':
    app.run()
