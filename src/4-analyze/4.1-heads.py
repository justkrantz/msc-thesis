#%%
"""
Analyze the heads of metamodel, compare with 25m heads:
- absolute error
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
#%% Import data
heads_2024_meta   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_202412312359_l*.idf")
heads_2053_meta   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_205312312359_l*.idf")
like = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
gdf  = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
heads_SS_OM_zarr = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\head_ss_t0.zarr")

# Process data
heads_SS_OM = heads_SS_OM_zarr["head"].drop("time").astype(np.float64)
heads_2024_meta_notime = heads_2024_meta.isel(time=0, drop=True)
heads_2053_meta_notime = heads_2053_meta.isel(time=0, drop=True)

# Import regridder & regrid original data
mean_regridder = imod.prepare.Regridder(method="mean")
heads_SS_OM_re = mean_regridder.regrid(heads_SS_OM, like=like)

# %% error
def er(expected, actual):
    re = actual - expected
    return re

error_meta24_OM = er(heads_SS_OM_re, heads_2024_meta_notime)
error_meta53_OM = er(heads_SS_OM_re, heads_2053_meta_notime)

heads_error_global_mean = error_meta53_OM.mean().compute()

#%% Clip data to area of Interest 
raster             = imod.prepare.rasterize(gdf, like) 
heads_2024_meta_clipped = heads_2024_meta.isel(time=0, drop=True).where(raster==1)
heads_2053_meta_clipped = heads_2053_meta.isel(time=0, drop=True).where(raster==1)
heads_SS_OM_clipped = heads_SS_OM_re.where(raster==1)

# error in study area (SA):
error_SA = er(heads_SS_OM_clipped, heads_2053_meta_clipped)
heads_error_SA_mean = error_SA.mean().compute()

#%% Plotting: 
levels_err  = np.arange(0,21)/2-5
levels_head = [-6.0, -5.5, -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0] 
# cross sections
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
#%%
# metamodel heads cross sections
plt.figure(figsize=(12,14))
plt.subplots_adjust(hspace=0.5)
plt.suptitle("hydraulic heads cross sections of metmamodel, perpendicular to coastline")
for i, (start, end) in enumerate(zip(starts, ends)):
    ax = plt.subplot(5,2, i+1)
    CS = imod.select.cross_section_line(heads_2053_meta, start=start, end=end)
    CS.plot(ax=ax, levels=levels_head, yincrease = False)
    plt.title(f"CS{i+1}, 2053 heads")
path = pathlib.Path(f"reports/images/CS_heads_meta.png")
plt.savefig(path, dpi=300)

# original model heads cross sections
plt.figure(figsize=(12,14))
plt.subplots_adjust(hspace=0.5)
plt.suptitle("hydraulic heads cross sections of original model, perpendicular to coastline")
for i, (start, end) in enumerate(zip(starts, ends)):
    ax = plt.subplot(5,2,i+1)
    CS = imod.select.cross_section_line(heads_SS_OM, start=start, end=end)
    CS.plot(ax=ax, levels=levels_head, yincrease = False)
    plt.title(f"CS{i+1}, 2053 heads")
path = pathlib.Path(f"reports/images/CS_heads_OM.png")
plt.savefig(path, dpi=300)
# %% Creating Cross sections next to eachother
plt.figure(figsize=(14,26))
plt.subplots_adjust(hspace=0.6)
plt.suptitle("hydraulic heads")
ax_OM = plt.axes()

for i, (start, end) in enumerate(zip(starts, ends)):
    ax_OM = plt.subplot(10,2, (i+1)*2, sharex=ax_OM)  # Set the position of the subplot 
    CS_OM = imod.select.cross_section_line(heads_SS_OM, start=start, end=end)
    CS_OM.plot(ax=ax_OM,y="z",  levels = levels_head)
    plt.title(f"CS{i+1} OM")
 #   plt.colorbar(ax=ax, label="conc")    

# one column set using indexing, rest manual:
ax1 = plt.subplot(10,2,1, sharex=ax_OM) # position 1 (top left)
CS2 = imod.select.cross_section_line(heads_2053_meta, start=starts[0], end=ends[0])
CS2.plot(ax=ax1,y="z",  levels = levels_head)
plt.title(f"CS1 Metamodel")

ax3 = plt.subplot(10,2,3, sharex=ax_OM) # position 3 (left)
CS2 = imod.select.cross_section_line(heads_2053_meta, start=starts[1], end=ends[1])
CS2.plot(ax=ax3,y="z",  levels = levels_head)
plt.title(f"CS2 Metamodel")

ax5 = plt.subplot(10,2,5, sharex=ax_OM) # position 5 (left)
CS2 = imod.select.cross_section_line(heads_2053_meta, start=starts[2], end=ends[2])
CS2.plot(ax=ax5,y="z",  levels = levels_head)
plt.title(f"CS3 Metamodel")

ax7 = plt.subplot(10,2,7, sharex=ax_OM) # position 7 (left)
CS2 = imod.select.cross_section_line(heads_2053_meta, start=starts[3], end=ends[3])
CS2.plot(ax=ax7,y="z",  levels = levels_head)
plt.title(f"CS4 Metamodel")

ax9 = plt.subplot(10,2,9, sharex=ax_OM) # position 9 (left)
CS2 = imod.select.cross_section_line(heads_2053_meta, start=starts[4], end=ends[4])
CS2.plot(ax=ax9,y="z",  levels = levels_head)
plt.title(f"CS5 Metamodel")
path_4 = pathlib.Path(f"reports/images/CS_heads_combined.png")
plt.savefig(path_4, dpi=200)
# %%
