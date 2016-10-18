import urllib.request
import urllib.parse
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

_query_url = 'http://gis.ncdc.noaa.gov/arcgis/rest/services/cdo/lcd_curr/MapServer/0/query'
_station_metadata_url = 'http://gis.ncdc.noaa.gov/arcgis/rest/services/cdo/lcd_curr/MapServer/0/{}?f=pjson'


def get_stations(xmin, xmax, ymin, ymax):
    data = {'returnGeometry': 'true',
            'inSR': '4326',
            'f': 'pjson',
            'geometry': '{{"xmax":{},"ymax":{},'
                         '"xmin":{},"ymin":{}}}'.format(xmax, ymax, xmin,ymin),
            'geometryType': 'esriGeometryEnvelope',
            'returnIdsOnly': 'true',
            'spatialRel': 'esriSpatialRelContains'
            }
    data = urllib.parse.urlencode(data).encode('ascii')
    response = urllib.request.urlopen(_query_url, data)
    response_decode = response.read().decode(response.info().get_param('charset') or 'utf-8')
    station_data = json.loads(response_decode)
    station_ids = station_data['objectIds']
    stations=[]
    for station_id in station_ids:
        response = urllib.request.urlopen(_station_metadata_url.format(station_id))
        response_decode = response.read().decode(response.info().get_param('charset') or 'utf-8')
        station_metadata = json.loads(response_decode)
        station_args = {a.lower():b for a,b in station_metadata['feature']['attributes'].items()}
        stations.append(WeatherStation(**station_args))
    return stations


class WeatherStation:
    data_url = 'http://www.ncdc.noaa.gov/qclcd/QCLCD'

    def __init__(self, wban, call_sign, latitude, longitude, **kwargs):
        self.wban = wban
        self.call_sign = call_sign
        self.lat = latitude
        self.lon = longitude
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "{call_sign} WBAN:{wban} at Lat:{lat} Lon:{lon}".format(**self.__dict__)

    def retrieve_data(self, year, month):
        params = {
            'reqday': 'E',
            'stnid': 'n/a',
            'prior': 'N',
            'qcname': 'VER2',
            'VARVALUE': '{}{:4d}{:02d}'.format(self.wban, year, month),
            'which': 'ASCII Download (Hourly Obs.) (10A)'
        }
        params = urllib.parse.urlencode(params).encode('ascii')
        response = urllib.request.urlopen(self.data_url, params)
        df = pd.read_csv(response, header=7, encoding='utf-8')
        df.dropna(inplace=True)
        dates = pd.to_datetime((df['Date']*10000+df['Time']).apply(int).apply(str))
        df.set_index(dates, inplace=True)
        df = df.convert_objects(convert_numeric=True)
        return df

stations = get_stations(-119.10124511718753, -118.09050292968753, 32.38557128906, 33.55561523437499)
for station in stations:
    df = station.retrieve_data(2016, 7)
    sns.distplot(df['WindSpeed'].dropna(), rug=True, bins=range(0,22,2), label='Win')
# plt.legend()
plt.show()