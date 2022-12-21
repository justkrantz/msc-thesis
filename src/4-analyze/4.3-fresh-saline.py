"""
Here the mean absolute error can be calculated for total area and area of interest
We can calculate the total volume of fresh water over time, 
or the depth of fresh water over time.

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
import geopandas
#%%
os.chdir("c:/projects/msc-thesis")
#%% 
mean_regridder = imod.prepare.Regridder(method="mean") 
# Import data
like   = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
ibound = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/ibound_coarse.nc") 
gdf    = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
surface_level = xr.open_dataarray("data/2-interim/surface_level_without_sea.nc")
# output data 
conc_OM    = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\conc-selection.zarr")["conc"].astype(np.float64)
conc_meta  = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c1*.IDF").isel(species=0,drop=True)
conc_meta = conc_meta.where(conc_meta != 1e30)
conc_meta = conc_meta.where(~(conc_meta < 0.0), other=0.0)
#%% Process data
conc_OM_39y   = mean_regridder.regrid(conc_OM.isel(time=-1,drop=True), like)   # note that the final date is 39y and 9 months, not 40y
conc_meta_40y = conc_meta.isel(time=-1, drop=True)
#%% Functions
def rel_er(expected, actual):
    act_abs = np.abs(actual)
    exp_abs = np.abs(expected)
    re = ((act_abs - exp_abs)/exp_abs)
    return re
def abs_er(expected, actual):
    ae = actual - expected
    return ae
#%% PLotting depth of fresh-brackish interface   
# Bounds for groundwater types
fresh_upper = 0.150   # g/l
brack_upper = 8.0000  # g/l

# Depth fresh water OM
layer_count_OM = conc_OM_39y.where(conc_OM_39y < fresh_upper).count("layer") 
depth_fresh_OM1 = ibound["z"].where(ibound["layer"]==layer_count_OM).min("z")
# Huite's help:
depth_fresh_OM2  = conc_OM["z"].where(conc_OM_39y < fresh_upper).min("layer")
depth_fresh_OM_H = depth_fresh_OM2.combine_first(surface_level) 

# Depth fresh water meta
layer_count_meta  = conc_meta_40y.where(conc_meta_40y < fresh_upper).count("layer") 
depth_fresh_meta1 = ibound["z"].where(ibound["layer"]==layer_count_meta).min("z")
# Huite's help:
depth_fresh_meta2  = conc_OM["z"].where(conc_meta_40y < fresh_upper).min("layer")
depth_fresh_meta_H = depth_fresh_meta2.combine_first(surface_level) 

#%% Plotting
levels_conc  = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]
levels_depth = -1 * np.arange(0,130)
levels_conc_err = np.arange(0,20)/2-5
# Cross sections
starts = [
    (75000.0, 459948.0), # (x,y)
    (77423.0, 462817.0),
    (79234.0, 464828.4),
    (81880.4, 467911.6),
    (83718.9, 469707.8),
]
ends = [
    (87591.0, 449868.0), # (x,y)
    (92828.2, 450002.0),
    (93914.6, 452120.1),
    (95223.9, 455793.2),
    (96393.9, 460431.4),
]

for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(conc_err_abs, start=start, end=end)
    ax = CS.plot(yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1}, meta perpendicular to coastline at t = 40y [d]")

# %%
