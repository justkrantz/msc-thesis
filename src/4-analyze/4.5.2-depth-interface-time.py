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
conc_MM  = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\4-scenario-200y-fixedrand\conc\conc_c1*.IDF").isel(species=0,drop=True)
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
    "2014-12-31T23:59:59.000000000", "2015-01-01T00:00:00.000000000","2020-01-01T00:00:00.000000000","2025-01-01T00:00:00.000000000",
    "2030-01-01T00:00:00.000000000", "2035-01-01T00:00:00.000000000","2040-01-01T00:00:00.000000000","2045-01-01T00:00:00.000000000",
    "2050-01-01T00:00:00.000000000", "2055-01-01T00:00:00.000000000","2060-01-01T00:00:00.000000000","2065-01-01T00:00:00.000000000","2070-01-01T00:00:00.000000000",
    "2075-01-01T00:00:00.000000000", "2080-01-01T00:00:00.000000000","2085-01-01T00:00:00.000000000","2090-01-01T00:00:00.000000000","2095-01-01T00:00:00.000000000",
    "2100-01-01T00:00:00.000000000", "2105-01-01T00:00:00.000000000","2110-01-01T00:00:00.000000000","2115-01-01T00:00:00.000000000",
    "2120-01-01T00:00:00.000000000", "2125-01-01T00:00:00.000000000","2130-01-01T00:00:00.000000000","2135-01-01T00:00:00.000000000",
    "2140-01-01T00:00:00.000000000", "2145-01-01T00:00:00.000000000","2150-01-01T00:00:00.000000000","2155-01-01T00:00:00.000000000",
    "2160-01-01T00:00:00.000000000", "2165-01-01T00:00:00.000000000","2170-01-01T00:00:00.000000000","2175-01-01T00:00:00.000000000", 
    "2180-01-01T00:00:00.000000000", "2185-01-01T00:00:00.000000000","2190-01-01T00:00:00.000000000","2195-01-01T00:00:00.000000000",
    "2200-01-01T00:00:00.000000000", "2205-01-01T00:00:00.000000000","2210-01-01T00:00:00.000000000","2215-01-01T00:00:00.000000000"], dtype="datetime64")
conc_MM_ar = dict()
depth_MM_ds = xr.Dataset()
for i in range(0,41):
    conc_MM_ar[i]  = conc_meta.isel(time=i, drop=True)
    depth_MM_ds[i] = conc_MM["z"].where(conc_MM_ar[i]<fresh_upper).where(raster==1).min("layer").mean().compute()
depth_MM_da = depth_MM_ds.to_array()
# %% PLOTTING
fig,ax = plt.subplots(sharex=True)
plt.plot(times[:41], depth_MM_da, color=(35/255 , 130/255, 183/255))
plt.title("")
plt.ylabel("depth [m]")
plt.ylim((-90,0))
plt.xlabel("time")
path = pathlib.Path(f"reports/images/4-scenario-200y-fixedrand/depth-interface_MM_200y.png")
plt.grid(axis="y")
#plt.savefig(path, dpi=200)

# %%
