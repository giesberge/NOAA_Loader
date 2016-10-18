import json
import urllib.request
import matplotlib.path as mplPath
import shutil
import os
import csv
from zipfile import ZipFile
from osgeo import ogr

with open('S57Acronyms.csv', 'r') as f:
    s57_acronyms = {k:v for k,v in csv.reader(f)}


class ChartList:
    def __init__(self):
        self.chart_list = []
        self.get_chart_list()

    def get_chart_list(self):
        chart_list = "http://www.charts.noaa.gov/InteractiveCatalog/data/enc.json"
        response = urllib.request.urlopen(chart_list)
        data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
        for chart in data['encs']:
            self.chart_list.append(Chart(**chart))

    def charts_with_point(self, lat, lon):
        charts_that_contain = []
        for chart in self.chart_list:
            if chart.contains_point(lat, lon):
                charts_that_contain.append(chart)
        return charts_that_contain


class Chart:
    def __init__(self, cnum, pdate, rnc, curEd, mbr, title, cl, points, scale, **kwargs):
        self.cnum = cnum
        self.pdate = pdate
        self.rnc = rnc
        self.curEd = curEd
        self.mbr = mbr
        self.title = title
        self.cl = cl
        self.scale = scale
        self.points = [(x,y) for x,y in zip(points[::2], points[1::2])]
        self.path = mplPath.Path(self.points)
        self.data_file = r"Data\{}.zip".format(self.cnum)
        self.tempfile = 'temp.{}.000'.format(self.cnum)

    def contains_point(self, lat, lon):
        return self.path.contains_point((lat, lon))

    def __repr__(self):
        return "{cnum} - {title} - {scale}".format(**self.__dict__)

    def download_map(self):
        dl_url = 'http://www.charts.noaa.gov/ENCs/{}.zip'.format(self.cnum)
        req = urllib.request.urlopen(dl_url)
        with open(self.data_file, 'wb') as fp:
            shutil.copyfileobj(req, fp)

    def get_datasource(self):
        driver = ogr.GetDriverByName("S57")
        if not os.path.exists(self.data_file):
            self.download_map()
        with ZipFile(self.data_file) as zip_data:
            file_path = r"ENC_ROOT/{}/{}.000".format(self.cnum, self.cnum)

            with open(self.tempfile, 'wb') as f:
                f.write(zip_data.read(file_path))
            ds = driver.Open(self.tempfile, False)
            return ds

    def layers(self):
        ds = self.get_datasource()
        layer_names = {}
        for layer in ds:
            layer_name = layer.GetName()
            layer_names[layer_name]=s57_acronyms.get(layer_name, '???')
        return layer_names

    def get_layer(self, layer):
        ds = self.get_datasource()
        layer_data = ds.GetLayerByName(layer)
        if layer_data is None:
            raise KeyError("Data source does not contain layer={}".format(layer))
        features =[]
        for feature in layer_data:
            features.append(feature.ExportToJson(True))
        return features

    def __del__(self):
        try:
            os.remove(self.tempfile)
        except FileNotFoundError:
            pass



if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.collections import PatchCollection
    from pprint import pprint

    clist = ChartList()
    chartmatch = clist.charts_with_point(32.9029, -118.4981)
    chart = chartmatch[2]
    pprint(chart.layers())
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
    plt.axis('equal')
    plt.axis('off')
    plt.show()