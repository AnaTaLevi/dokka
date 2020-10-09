import ast
from io import StringIO
from math import radians, sin, cos, atan2, sqrt

import pandas as pd
import requests
import json
import itertools
import uuid

import fieldNames
import serviceDA
from point import Point

encoding = 'utf-8'

# approximate radius of earth in km
R = 6373.0

api_link = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?location={0}%2C{' \
           '1}&langCode=en&outSR=&forStorage=false&f=pjson'

points = []
points_to_distance = {}


def get_address_from_api(latitude, longitude):
    url = api_link.format(latitude, longitude)
    response = requests.get(url)
    json_response = json.loads(response.text)
    address = json_response[fieldNames.ADDRESS][fieldNames.LONG_LABEL]
    return address


def get_distance(a, b):
    lat1 = radians(a.latitude)
    lon1 = radians(a.longitude)
    lat2 = radians(b.latitude)
    lon2 = radians(b.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def init_points_to_distance():
    points_permutations = list(itertools.combinations(points, 2))
    for a, b in points_permutations:
        name = min(a.name, b.name) + max(a.name, b.name)
        distance = serviceDA.get_distance_from_db(name)
        if not distance:
            distance = get_distance(a, b)
            serviceDA.persist_distance(name, distance)
        points_to_distance[name] = distance


def dict_to_json():
    res = {fieldNames.POINTS: [], fieldNames.LINKS: []}
    new_uuid = uuid.uuid4().hex
    for point in points:
        item = {fieldNames.NAME: point.name, fieldNames.ADDRESS: point.address}
        res[fieldNames.POINTS].append(item)

    for name, distance in points_to_distance.items():
        item = {fieldNames.NAME: name, fieldNames.DISTANCE: distance}
        res[fieldNames.LINKS].append(item)

    res[fieldNames.RESULT_ID] = new_uuid
    serviceDA.persist_result(new_uuid, str(res))
    return res


def file_to_json(file):
    s = str(file, encoding)
    data = StringIO(s)
    df = pd.read_csv(data)
    for _, loc in df.T.iteritems():
        latitude = loc.Latitude
        longitude = loc.Longitude
        name = loc.Point
        address = serviceDA.get_address_from_db(name)
        if not address:
            address = get_address_from_api(latitude, longitude)
            serviceDA.persist_point(name, latitude, longitude, address)
        point = Point(name, address, latitude, longitude)
        points.append(point)
    init_points_to_distance()
    output_json = dict_to_json()
    return output_json


def get_result(uuid):
    res = serviceDA.get_result(uuid)
    res = ast.literal_eval(res)
    return res
