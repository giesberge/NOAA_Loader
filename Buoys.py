import urllib.parse
import urllib.request
import re
import concurrent.futures
import json


def refresh_station_list():
    buoy_list = 'http://www.ndbc.noaa.gov/ndbcmapstations.json'
    response = urllib.request.urlopen(buoy_list)
    data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
    for station in data['station']:
        buoy = Buoy(**station)
        print(buoy)


class Buoy:
    def __init__(self, id, lat, lon, name, data=False, **kwargs):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.name = name
        self.data = data
        print(kwargs['owner'])

    def __repr__(self):
        return "Station #{id}: {name} at Lat:{lat} Long:{lon} {data}".format(**self.__dict__)


if __name__ == "__main__":
    refresh_station_list()