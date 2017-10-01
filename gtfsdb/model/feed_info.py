import json

from sqlalchemy import Column
from sqlalchemy.types import Date, String

from gtfsdb import config
from gtfsdb.model.base import Base


class FeedInfo(Base):
    datasource = config.DATASOURCE_GTFS
    filename = 'feed_info.txt'

    __tablename__ = 'feed_info'

    feed_publisher_name = Column(String(255), primary_key=True)
    feed_publisher_url = Column(String(255), nullable=False)
    feed_lang = Column(String(255), nullable=False)
    feed_start_date = Column(Date)
    feed_end_date = Column(Date)
    feed_version = Column(String(255))
    feed_license = Column(String(255))

    def to_dict(self):
        fields = {
            'feed_publisher_name': self.feed_publisher_name,
            'feed_publisher_url': self.feed_publisher_url,
            'feed_lang': self.feed_lang,
            'feed_start_date': self.feed_start_date,
            'feed_end_date': self.feed_end_date,
            'feed_version': self.feed_version,
            'feed_license': self.feed_license
        }
        return fields

    def to_json(self):
        return json.dumps(self.to_dict())
