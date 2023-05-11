"""
In this script the depth of the fresh-saline interface will be plotted over time:
    - Study area
    - 200y run
To retrieve an equilibrium depth and for plotting.
"""
#%%
import numpy as np
import os
import imod
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import geopandas
import matplotlib.patches as mpatches
#%%
os.chdir("c:/projects/msc-thesis")
# %% Import Data
conc_MM  = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\3-scenario_FixedHead_rand\conc\conc_c1*.IDF").isel(species=0,drop=True)
gdf    = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
like   = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
#%% Process data

raster        = imod.prepare.rasterize(gdf, like) 
# Define f/s interface
fresh_upper = 0.150   # g/l
brack_upper = 8.0000  # g/l
# Remove negative concentrations
conc_meta = conc_MM.where(conc_MM != 1e30)
conc_meta = conc_meta.where(~(conc_meta < 0.0), other=0.0)

# index the conc dataset per timestep
times=np.array([
    "2015-01-01T00:00:00.000000000", "2020-01-01T00:00:00.000000000", "2025-01-01T00:00:00.000000000", 
    "2030-01-01T00:00:00.000000000", "2035-01-01T00:00:00.000000000", "2040-01-01T00:00:00.000000000", "2045-01-01T00:00:00.000000000", 
    "2050-01-01T00:00:00.000000000","2055-01-01T00:00:00.000000000"], dtype="datetime64")
conc_MM_ar = dict()
depth_MM_ds = xr.Dataset()
for i in range(0,9):
    conc_MM_ar[i]  = conc_meta.isel(time=i, drop=True)
    depth_MM_ds[i] = conc_MM["z"].where(conc_MM_ar[i]<fresh_upper).where(raster==1).min("layer").mean().compute()
depth_MM_da = depth_MM_ds.to_array()
# %% PLOTTING
fig,ax = plt.subplots(sharex=True)
plt.plot(times, depth_MM_da, color="orange")
plt.title("Depth of fresh-saline interface Scenario 3")
plt.ylabel("depth [m]")
plt.ylim((-80,-50))
plt.xlabel("Time")
path = pathlib.Path(f"reports/images/3-scenario_FixedHead_rand/depth-interface_MM_40y.png")
plt.savefig(path, dpi=200)

# %%