from flask import send_file, Response, request, url_for, redirect
from app import app

from menetrend.graph import *
from menetrend.trip_planner import *
from menetrend.routes import *
from menetrend.schedule import *
from menetrend.trips import *
from menetrend.stops import *

import json


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return redirect(url_for('static', filename='favicon.ico'), code=302)


@app.route('/')
def index():
    return send_file('templates/index.html')


@app.route('/get_bus_routes', methods=['GET'])
@cache.cached(timeout=86400)
def get_bus_routes():
    bus_routes = query_routes_by_route_type(3)

    response = Response(response=json.dumps(bus_routes), status=200, mimetype='application/json')
    return response


@app.route('/get_tram_routes', methods=['GET'])
@cache.cached(timeout=86400)
def get_tram_routes():
    tram_routes = query_routes_by_route_type(0)

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

    trip = test_route_short_name(route_short_name, direction_id)

    if trip is None:
        response = Response(status=404)
        return response

    trips, trips_dict = query_trips_schedule(route_short_name, direction_id, date, trip)

    if not trips:
        response = Response(response=json.dumps(trips_dict), status=400)
        return response

    scheduled_trips_dict = generate_schedule_dictionary(trips, trips_dict)

    response = Response(response=json.dumps(scheduled_trips_dict), status=200, mimetype='application/json')
    return response


@app.route('/get_dates', methods=['GET'])
def get_dates():
    dates = query_dates()

    response = Response(response=json.dumps(dates), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_stops', methods=['GET'])
def get_trip_stops():
    trip_id = request.args.get('trip_id')
    trip = test_trip(trip_id)

    if trip is None:
        response = Response(status=400)
        return response

    trip_dict = query_trip_stops(trip)

    response = Response(response=json.dumps(trip_dict), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_shapes', methods=['GET'])
def get_trip_shapes():
    trip_id = request.args.get('trip_id')
    trip = test_trip(trip_id)

    if trip is None:
        response = Response(status=400)
        return response

    shapes = query_trip_shapes(trip)

    response = Response(response=json.dumps(shapes), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_stops_coordinates', methods=['GET'])
def get_trip_stops_coordinates():
    trip_id = request.args.get('trip_id')
    trip = test_trip(trip_id)

    if trip is None:
        response = Response(status=400)
        return response

    trip_stops_coordinates = query_trip_stops_coordinates(trip)

    response = Response(response=json.dumps(trip_stops_coordinates), status=200, mimetype='application/json')
    return response


@app.route('/get_trip_terminals_coordinates', methods=['GET'])
def get_trip_terminals_coordinates():
    trip_id = request.args.get('trip_id')
    trip = test_trip(trip_id)

    if trip is None:
        response = Response(status=400)
        return response

    trip_terminals_coordinates = query_trip_terminals_coordinates(trip)

    response = Response(response=json.dumps(trip_terminals_coordinates), status=200, mimetype='application/json')
    return response


@app.route('/get_all_stops', methods=['GET'])
def get_all_stops():
    stops = query_all_stops()

    response = Response(response=json.dumps(stops), status=200, mimetype='application/json')
    return response


@app.route('/plan_trip', methods=['POST'])
def plan_trip():
    request_data = request.json
    graph = generate_graph()
    if request_data['from'] == request_data['to']:
        response = Response(status=400)
        return response
    try:
        path, cost = dijkstra(graph, {'name': request_data['from'], 'route': None}, request_data['to'], visited=[],
                              distances={}, predecessors={})
        response = Response(response=json.dumps(path), status=200, mimetype='application/json')
        return response
    except TypeError:
        response = Response(status=400)
        return response


if __name__ == '__main__':
    app.run()
