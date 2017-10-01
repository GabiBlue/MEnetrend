import json

from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


__all__ = ['StopFeature']


class StopFeature(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'stop_features.txt'

    __tablename__ = 'stop_features'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True)
    stop_id = Column(String(255), index=True, nullable=False)
    feature_type = Column(String(50), index=True, nullable=False)
    feature_name = Column(String(255))

    def to_dict(self):
        fields = {
            'id': self.id,
            'stop_id': self.stop_id,
            'feature_type': self.feature_type,
            'feature_name': self.feature_name
        }
        return fields

    def to_json(self):
        return json.dumps(self.to_dict())
