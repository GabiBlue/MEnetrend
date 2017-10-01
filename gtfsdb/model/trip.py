import logging
import json
log = logging.getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base



class Trip(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'trips.txt'

    __tablename__ = 'trips'

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    route_id = Column(String(255), index=True, nullable=False)
    service_id = Column(String(255), index=True, nullable=False)
    direction_id = Column(Integer, index=True)
    block_id = Column(String(255), index=True)
    shape_id = Column(String(255), index=True, nullable=True)
    trip_type = Column(String(255))

    trip_headsign = Column(String(255))
    trip_short_name = Column(String(255))
    bikes_allowed = Column(Integer, default=0)
    wheelchair_accessible = Column(Integer, default=0)

    pattern = relationship(
        'Pattern',
        primaryjoin='Trip.shape_id==Pattern.shape_id',
        foreign_keys='(Trip.shape_id)',
        uselist=False, viewonly=True)

    route = relationship(
        'Route',
        primaryjoin='Trip.route_id==Route.route_id',
        foreign_keys='(Trip.route_id)',
        uselist=False, viewonly=True)

    stop_times = relationship(
        'StopTime',
        primaryjoin='Trip.trip_id==StopTime.trip_id',
        foreign_keys='(Trip.trip_id)',
        order_by='StopTime.stop_sequence',
        uselist=True, viewonly=True)

    universal_calendar = relationship(
        'UniversalCalendar',
        primaryjoin='Trip.service_id==UniversalCalendar.service_id',
        foreign_keys='(Trip.service_id)',
        uselist=True, viewonly=True)

    @classmethod
    def post_process(cls, db, **kwargs):
        trips = db.session.query(Trip).all()
        for t in trips:
            if not t.is_valid:
                log.warn("invalid trip: {0} only has {1} stop_time record (i.e., maybe the stops are coded as "
                         "non-public, and thus their stop time records didn't make it into the gtfs)"
                         .format(t.trip_id, t.trip_len))

    @property
    def start_stop(self):
        return self.stop_times[0].stop

    @property
    def end_stop(self):
        return self.stop_times[-1].stop

    @property
    def start_time(self):
        return self.stop_times[0].departure_time

    @property
    def end_time(self):
        return self.stop_times[-1].arrival_time

    @property
    def trip_len(self):
        ret_val = 0
        if self.stop_times:
            ret_val = len(self.stop_times)
        return ret_val

    @property
    def is_valid(self):
        # trip has to have multiple stop times to be valid, else it's not a trip...
        return self.trip_len >= 2

    def to_dict(self):
        fields = {
            'trip_id': self.trip_id,
            'route_id': self.route_id,
            'service_id': self.service_id,
            'direction_id': self.direction_id,
            'block_id': self.block_id,
            'shape_id': self.shape_id,
            'trip_type': self.trip_type,
            'trip_headsign': self.trip_headsign,
            'trip_short_name': self.trip_short_name,
            'bikes_allowed': self.bikes_allowed,
            'wheelchair_accessible': self.wheelchair_accessible
        }
        return fields

    def to_json(self):
        return json.dumps(self.to_dict())