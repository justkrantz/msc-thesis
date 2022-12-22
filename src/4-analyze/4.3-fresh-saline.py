"""
Here the mean error can be calculated for total area and area of interest
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
conc_meta_39y = conc_meta.isel(time=-1, drop=True)
raster        = imod.prepare.rasterize(gdf, like) 
#%% Functions
def rel_er(expected, actual):
    act_abs = np.abs(actual)
    exp_abs = np.abs(expected)
    re = ((act_abs - exp_abs)/exp_abs)
    return re
def er(expected, actual):
    er = actual - expected
    return er
#%% PLotting depth of fresh-brackish interface   
# Bounds for groundwater types
fresh_upper = 0.150   # g/l
brack_upper = 8.0000  # g/l

# Depth fresh-saline interface OM
depth_fresh_OM2  = conc_OM["z"].where(conc_OM_39y < fresh_upper).min("layer")
depth_fresh_OM_H = depth_fresh_OM2.combine_first(surface_level) 

# Depth fresh-saline interface meta
depth_fresh_meta2  = conc_OM["z"].where(conc_meta_39y < fresh_upper).min("layer")
depth_fresh_meta_H = depth_fresh_meta2.combine_first(surface_level) 

error_depth = er(depth_fresh_OM_H, depth_fresh_meta_H)
error_depth_study_area = error_depth.where(raster==1)
#%%
# Plotting & saving depth of interface
levels_depth = -1 * np.arange(0,130)
fig,(ax1, ax2, ax3) = plt.subplots(3,1, sharex=True, sharey=True, figsize=(6,12))
depth_fresh_meta_H.plot.imshow(ax=ax1,cmap="turbo", levels=levels_depth)
ax1.set_title("Metamodel")
depth_fresh_OM_H.plot.imshow(ax=ax2, cmap="turbo", levels=levels_depth)
ax2.set_title("Original model")
error_depth.plot.imshow(ax=ax3)
ax3.set_title("Error of the metamodel")
path = pathlib.Path(f"reports/images/depth_freshwater.png")
path.parent.mkdir(exist_ok=True, parents=True)
fig.savefig(path, dpi=300)

#%% Plotting - cross sections salinity
levels_conc  = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]
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

# Original model

plt.figure(figsize=(15,15))
plt.subplots_adjust(hspace=0.5)
plt.suptitle("Groundwater salinity [Cl-] of original model")
for i, (start, end) in enumerate(zip(starts, ends)):
    ax = plt.subplot(5,2,i+1)
    CS = imod.select.cross_section_line(conc_OM_39y, start=start, end=end)
    CS.plot(ax=ax,y="z", yincrease = False, cmap = "turbo", levels = levels_conc)
    plt.title(f"CS{i+1},perpendicular to coastline, after 39y")
path_3 = pathlib.Path(f"reports/images/CS_salinity_OM.png")
plt.savefig(path_3, dpi=300)

# Metamodel

plt.figure(figsize=(15,15))
plt.subplots_adjust(hspace=0.5)
plt.suptitle("Groundwater salinity [Cl-] of metamodel")
for i, (start, end) in enumerate(zip(starts, ends)):
    ax = plt.subplot(5,2,i+1)
    CS = imod.select.cross_section_line(conc_meta_39y, start=start, end=end)
    CS.plot(ax=ax,y="z", yincrease = False, cmap = "turbo", levels = levels_conc)
    plt.title(f"CS{i+1}, perpendicular to coastline after 39y")
path_3 = pathlib.Path(f"reports/images/CS_salinity_meta.png")
plt.savefig(path_3, dpi=300)

