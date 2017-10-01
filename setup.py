from gtfsdb.api import database_load
from pkg_resources import resource_filename
import os

if __name__ == '__main__':
    path = resource_filename('gtfsdb', 'zips')
    gtfs_file = 'file:///{0}'.format(os.path.join(path, 'mvkzrt.zip'))
    basedir = os.path.abspath(os.path.dirname(__file__))
    url = 'sqlite:///' + os.path.join(basedir, 'mvk.db')
    db = database_load(gtfs_file, url=url)
