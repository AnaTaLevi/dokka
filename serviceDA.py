from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

import fieldNames

db_path = 'sqlite:////Users/anat/anat_db.db'

engine = create_engine(db_path)
Base = declarative_base()


def get_address_from_db(name):
    with engine.connect() as connection:
        query = 'select * from points where name="{0}"'.format(name)
        result = connection.execute(query)
        for row in result:
            return row[fieldNames.ADDRESS]


def get_distance_from_db(path):
    with engine.connect() as connection:
        query = 'select * from distances where path="{0}"'.format(path)
        result = connection.execute(query)
        for row in result:
            return row[fieldNames.DISTANCE]


def get_result(uuid):
    with engine.connect() as connection:
        query = 'select * from results where uuid="{0}"'.format(uuid)
        result = connection.execute(query)
        for row in result:
            return row[fieldNames.JSON]


def persist_point(name, latitude, longitude, address):
    with engine.connect() as connection:
        query = 'insert into points values ("{0}", "{1}", "{2}", "{3}")' \
            .format(name, latitude, longitude, address)
        result = connection.execute(query)
    return result


def persist_distance(path, distance):
    with engine.connect() as connection:
        query = '''insert into distances values ("{0}", "{1}")'''.format(path, distance)
        result = connection.execute(query)
    return result


def persist_result(uuid, res):
    with engine.connect() as connection:
        query = '''insert into results values ("{0}", "{1}")'''.format(uuid, res)
        result = connection.execute(query)
    return result

