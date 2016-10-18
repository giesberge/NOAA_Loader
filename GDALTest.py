import gdal
from gdalconst import *
from PIL import Image
from datetime import datetime
import numpy as np
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import osr
from Charts import ChartList
# driver = gdal.GetDriverByName('BSB')
# driver.Register()
# gdal.AllRegister()

file = r"G:\Downloads\multi_1.wc_4m.wind.201507.grb2"
# file = r"G:\Downloads\multi_1.glo_30m.wind.201506.grb2"
ds = gdal.Open(file, GA_ReadOnly)

if ds is None:
    print("Could not open {}".format(file))
    exit(1)

for i in range(1, ds.RasterCount+1):
    band = ds.GetRasterBand(i)
    metadata = band.GetMetadata()
    # print(metadata)
    band_level = metadata['GRIB_SHORT_NAME']
    band_variable = metadata['GRIB_ELEMENT']
    band_comment = metadata['GRIB_COMMENT']
    print(datetime.fromtimestamp(float(metadata['GRIB_VALID_TIME'].strip()[:10])))
    print(i, band_level, band_variable, band_comment)

data = band.ReadAsArray()
gt = ds.GetGeoTransform()
proj = ds.GetProjection()

xres = gt[1]
yres = gt[5]

# get the edge coordinates and add half the resolution
# to go to center coordinates
xmin = gt[0] + xres * 0.5
xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
ymax = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
ymin = gt[3] - yres * 0.5

print(xmin,xmax, ymin, ymax)

x1,y1 = np.meshgrid(np.linspace(xmin, xmax, ds.RasterXSize), np.linspace(ymin, ymax, ds.RasterYSize))
# for i in range(1, 250):
band_u = ds.GetRasterBand(1)
band_v = ds.GetRasterBand(251)
u = band_u.ReadAsArray(0,0,band_u.XSize, band_u.YSize)
v = band_v.ReadAsArray(0,0,band_u.XSize, band_u.YSize)
# u[u==9999]=0
# v[v==9999]=0
M = np.zeros(u.shape)
M[u==9999]=1
M[v==9999]=1
print(np.size(M)-np.sum(M))

import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection

clist = ChartList()
chartmatch = clist.charts_with_point(32.9029, -118.4981)
chart = chartmatch[2]
feats = chart.get_layer('LNDARE')

areas = []
for feat in feats:
    # print((feat['properties']['DRVAL1'], feat['properties']['DRVAL2']))
    geometry = feat['geometry']
    if geometry['type'] == 'Polygon':
        for coords in geometry['coordinates']:
            coords = geometry['coordinates'][0]
            areas.append(mpatches.Polygon(coords, closed=True))
collect = PatchCollection(areas)
collect.set_facecolors('none')
collect.set_edgecolor('b')
collect.set_linewidth(1)
fig = plt.figure(facecolor="white")
ax = plt.axes()
ax.add_collection(collect)
ymax, xmax, = np.max(np.array(chart.points), axis=0)
ymin, xmin = np.min(np.array(chart.points), axis=0)
plt.grid()

u_masked = np.ma.masked_array(u, mask=M)
v_masked = np.ma.masked_array(v, mask=M)
x1_masked = np.ma.masked_array(x1, mask=M)
y1_masked = np.ma.masked_array(y1, mask=M)
print(np.mean(u_masked), np.mean(v_masked))
p=2
add=0
plt.quiver(x1_masked[::p,::p]-360, y1_masked[::p,::p], u_masked[::p,::p], v_masked[::p,::p], units='y', scale=10,
           pivot='mid')
plt.axis('equal')
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.show()