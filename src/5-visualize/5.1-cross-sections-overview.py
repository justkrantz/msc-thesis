"""
Give a top view plot of the cross sections:
    - along coastline (see 4.1, 4.3)
    - perpendicular to coastline (see 4.4)
"""
#%%
import numpy as np
import os
import imod
import xarray as xr
import matplotlib.pyplot as plt
import scipy.ndimage.morphology
import pandas as pd
import pathlib
import geopandas as gpd
from shapely.geometry import Point, LineString
import contextily as cx

#%%
os.chdir("c:/projects/msc-thesis")
#%%
starts = [
    (75000.0, 459948.0), # CS1
    (77423.0, 462817.0),
    (79234.0, 464828.4),
    (81880.4, 467911.6),
    (83718.9, 469707.8),
]
ends = [
    (87591.0, 449868.0), # CS1
    (92828.2, 450002.0),
    (93914.6, 452120.1),
    (95223.9, 455793.2),
    (96393.9, 460431.4),
]

CS1_s = Point(starts[0])
CS1_f = Point(ends[0])

CS2_s = Point(starts[1])
CS2_f = Point(ends[1])

CS3_s = Point(starts[2])
CS3_f = Point(ends[2])

CS4_s = Point(starts[3])
CS4_f = Point(ends[3])

CS5_s = Point(starts[4])
CS5_f = Point(ends[4])

CS1 = LineString([CS1_s, CS1_f])
CS2 = LineString([CS2_s, CS2_f])
CS3 = LineString([CS3_s, CS3_f])
CS4 = LineString([CS4_s, CS4_f])
CS5 = LineString([CS5_s, CS5_f])

gdf = gpd.GeoDataFrame(data={"Cross section":["CS1", "CS2", "CS3", "CS4", "CS5"]}, geometry=[CS1, CS2, CS3, CS4, CS5])
gdf.crs = "EPSG:28992"
gdf_wm = gdf.to_crs(gdf.crs, epsg=28992)

ax=gdf.plot(figsize=(12,12))
cx.add_basemap(ax, crs="EPSG:28992")
ax.set_axis_off()
ax.set_title("Cross sections perpendicular to coastline")

# %% CS ALONG COASTLINE - See (4.4-Species)

start_loosduinen = Point(75471,453198)
end_katwijk      = Point(87789.1,468649.0)
CS_long = LineString([start_loosduinen, end_katwijk])

long = gpd.GeoDataFrame(data={"Cross section along coastline"}, geometry=[CS_long])
long.crs = "EPSG:28992"
long_wm = long.to_crs(long.crs, epsg=28992)

ax=long.plot(figsize=(12,12))
cx.add_basemap(ax, crs="EPSG:28992")
ax.set_axis_off()
ax.set_title("Cross sections along to coastline")

# %%
