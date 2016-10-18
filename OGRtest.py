from osgeo import ogr
# from pprint import pprint as print
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import csv


filename = r"G:\Downloads\US3CA70M\US3CA70M.000"
ds = driver.Open(r"G:\Downloads\US3CA70M\US3CA70M.000", 0)
print(type(ds))
with open('S57Acronyms.csv', 'r') as f:
    s57_acronyms = {k:v for k,v in csv.reader(f)}

for layer in ds:
    layer_name = layer.GetName()
    print("{}:{}".format(layer_name, s57_acronyms.get(layer_name, '???')))

fig = plt.figure(facecolor="white")
for layer in ds:
    ax = plt.axes()
    if layer.GetName() not in ["DEPARE"]:
        continue
    print(layer.GetName())
    areas = []
    for feature in layer:
        try:
            print((feature.ExportToJson(True)['properties']['DRVAL1'], feature.ExportToJson(True)['properties']['DRVAL2']))
        except:
            pass
        if not feature.GetGeometryRef():
            print("No geometry")
            continue
        for geometry in feature.GetGeometryRef():
            if geometry.GetGeometryName() == 'LINEARRING':
                # print("POLY!")
                coords = geometry.GetPoints()
                areas.append(mpatches.Polygon(coords + [coords[0]], closed=True))
            else:
                print(geometry.GetGeometryName())
    if len(areas) == 0:
        continue
    collect = PatchCollection(areas)
    collect.set_facecolors('none')
    if layer.GetName() == 'DEPARE':
        collect.set_edgecolor('b')
        collect.set_linewidth(0.1)
    ax.add_collection(collect)
plt.axis('equal')
plt.axis('off')
plt.show()