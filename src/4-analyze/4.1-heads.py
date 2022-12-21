#%%
"""
Analyze the heads of metamodel, compare with 25m heads:
- relative error
- study area relative error

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
import xskillscore as xs #for RMSE
#%%
os.chdir("c:/projects/msc-thesis")
#%% Import data
heads_2024_meta   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_202412312359_l*.idf")
heads_2054_meta   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_205412312359_l*.idf")
like         = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
gdf          = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
heads_SS_OM_zarr = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\head_ss_t0.zarr")

# Process data
heads_SS_OM = heads_SS_OM_zarr["head"].drop("time").astype(np.float64)
heads_2024_meta_notime = heads_2024_meta.isel(time=0, drop=True)
heads_2054_meta_notime = heads_2054_meta.isel(time=0, drop=True)

# Import regridder & regrid original data
mean_regridder = imod.prepare.Regridder(method="mean")
heads_SS_OM_re = mean_regridder.regrid(heads_SS_OM, like=like)

# %% absolute error
def abs_er(expected, actual):
    re = actual - expected
    return re

#%% Absolute error
abs_er_meta24_OM = abs_er(heads_SS_OM_re, heads_2024_meta_notime)
abs_er_meta54_OM = abs_er(heads_SS_OM_re, heads_2054_meta_notime)
# Root Mean Square error
#RMSE_2024 = xs.rmse(heads_SS_OM_re, heads_2024_meta_notime)
#RMSE_2054 = xs.rmse(heads_SS_OM_re, heads_2054_meta_notime)
#%% Clip data to area of Interest 
raster             = imod.prepare.rasterize(gdf, like) 
heads_2024_meta_clipped = heads_2024_meta.isel(time=0, drop=True).where(raster==1)
heads_2054_meta_clipped = heads_2054_meta.isel(time=0, drop=True).where(raster==1)
heads_SS_OM_clipped = heads_SS_OM_re.where(raster==1)

# absolute error in study area (SA):
abs_er_SA = abs_er(heads_SS_OM_clipped, heads_2054_meta_clipped)
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
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(abs_er_meta54_OM, start=start, end=end)
    ax = CS.plot(levels=levels_err, yincrease = False, cmap="turbo")
    plt.title(f"Conc: CS {i+1}, absolute error, metamodel and 2054 heads")
    
#%% meta model and 2054 heads

for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(heads_SS_OM, start=start, end=end)
    ax = CS.plot(levels=levels_head, yincrease = False)
    plt.title(f"heads: CS {i+1},OM SS heads")

# %%
