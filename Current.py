import netCDF4
import urllib.request
import urllib.parse
import numpy as np
from functools import partial

query = [
    ('var', 'u'),
    ('var', 'v'),
    ('north', '33.55'),
    ('west', '-119.3600'),
    ('east', '-117.1055'),
    ('south', '32.2500'),
    ('horizStride', '1'),
    ('time_start', '2016-09-16T00:00:00Z'),
    ('time_end', '2016-09-19T17:00:00Z'),
    ('timeStride', '1'),
    ('accept', 'netcdf')
]
_query_url = 'http://hfrnet.ucsd.edu/thredds/ncss/grid/HFR/USWC/2km/hourly/RTV/HFRADAR,_US_West_Coast,_2km_Resolution,_Hourly_RTV_best.ncd'
data = urllib.parse.urlencode(query).encode('ascii')
local_filename, headers = urllib.request.urlretrieve(_query_url, "Data/Temp.nc", data=data)
ncfile = netCDF4.Dataset(local_filename)
urllib.request.urlcleanup()
timestamps = [netCDF4.num2date(a, ncfile['time'].units).timestamp() for a in ncfile['time'][:]]
