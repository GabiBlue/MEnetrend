import json

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Frequency(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'frequencies.txt'

    __tablename__ = 'frequencies'

    trip_id = Column(String(255), primary_key=True)
    start_time = Column(String(8), primary_key=True)
    end_time = Column(String(8))
    headway_secs = Column(Integer)
    exact_times = Column(Integer)

    trip = relationship(
        'Trip',
        primaryjoin='Frequency.trip_id==Trip.trip_id',
        foreign_keys='(Frequency.trip_id)',
        uselist=False, viewonly=True)

    def to_dict(self):
        fields = {
            'trip_id': self.trip_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'headway_secs': self.headway_secs,
            'exact_times': self.exact_times
        }
        return fields

    def to_json(self):
        return json.dumps(self.to_dict())
