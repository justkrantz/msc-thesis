"""""
Create a cross section that shows the Surface level, and the hydraulic heads of the 25m, and 50m
NOT YET WORKING
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
#%% Import data
heads_2024_meta   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_202412312359_l*.idf")
heads_2053_meta   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_205312312359_l*.idf")
like = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
heads_SS_OM_zarr = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\head_ss_t0.zarr")
conductivity  = xr.open_dataset("data/1-external/conductivity.nc")


# Process data
heads_2053_meta_notime = heads_2053_meta.isel(time=0, drop=True)
# Set up Surface level
kh       = conductivity["kh"]
domain2d = heads_SS_OM_zarr.isel(layer=-1, drop =True).notnull()
ibound   = kh.notnull() & domain2d
top     = ibound.coords["ztop"]
top3d   = top.where(ibound != 0 )
surface_level = top3d.max("z")
sl_da = surface_level["head"]

# %% Cross section
# over dunes high, polders low
start = (82815.0,465206.0)
end   = (97066.0,455072.0)
CS_start = Point(82815.0,465206.0)
CS_end   = Point(97066.0,455072.0)

# Top view plot of location of CS
CS = LineString([CS_start, CS_end])
long = gpd.GeoDataFrame(data={"Cross section along coastline"}, geometry=[CS])
long.crs = "EPSG:28992"
long_wm = long.to_crs(long.crs, epsg=28992)
ax=long.plot(figsize=(12,12))
cx.add_basemap(ax, crs="EPSG:28992")
ax.set_axis_off()
ax.set_title("Cross section for surface level")
#%%
# Surface levl
CS_SL = imod.select.cross_section_linestring(sl_da, CS) # Not working.
sl_da.isel(y=330).plot()                                # is working. WHY?

#%%
# MM head
CS_head_meta = imod.select.cross_section_line(heads_2053_meta_notime, start=start, end=end) # Not working
CS_head_meta.plot(yincrease = False)


# %%
