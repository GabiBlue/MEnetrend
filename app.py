from flask import Flask
from flask.ext.cache import Cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('sqlite:///' + os.path.join(basedir, 'mvk.db'), echo=False)
Session = sessionmaker(bind=engine)
session = Session()
