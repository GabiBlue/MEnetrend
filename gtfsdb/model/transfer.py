import json

from sqlalchemy import Column,  Sequence
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class Transfer(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'transfers.txt'

    __tablename__ = 'transfers'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    from_stop_id = Column(String(255))
    to_stop_id = Column(String(255))
    transfer_type = Column(Integer, index=True, default=0)
    min_transfer_time = Column(Integer)

    def to_dict(self):
        fields = {
            'id': self.id,
            'from_stop_id': self.from_stop_id,
            'to_stop_id': self.to_stop_id,
            'transfer_type': self.transfer_type,
            'min_transfer_time': self.min_transfer_time
        }
        return fields

    def to_json(self):
        return json.dumps(self.to_dict())
