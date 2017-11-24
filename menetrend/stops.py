from app import session
from gtfsdb.model.stop import Stop


def query_all_stops():
    stops_result = session.query(Stop).group_by(Stop.stop_name).all()
    stops = [i.to_dict() for i in stops_result]

    return stops
