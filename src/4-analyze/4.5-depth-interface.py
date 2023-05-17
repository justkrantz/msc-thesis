"""
In this script the depth of the fresh-saline interface will be plotted over time for the study area, various scenarios
 - the idea is to come to an understanding of the artificial infiltration in the dune area,
    specifically the how much time it takes for freshwater to infiltrate  to a certain depth.

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
import matplotlib.patches as mpatches
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

conc_meta  = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\3-scenario_FixedHead_rand\conc\conc_c*.IDF").isel(species=0,drop=True)
conc_meta = conc_meta.where(conc_meta != 1e30)
conc_meta = conc_meta.where(~(conc_meta < 0.0), other=0.0)
#%% Process data
raster        = imod.prepare.rasterize(gdf, like) 
# Bounds for groundwater types
fresh_upper = 0.300   # g/l
brack_upper = 10.0000  # g/l
    
#%% Process data OM For study area
# NOTE: Regridding necessary to use the raster. the raster for the study area for 25m model can be found in 4.2 budgets waterbalance
conc_OM_1979   = mean_regridder.regrid(conc_OM.isel(time=0), like).where(raster==1)
conc_OM_1989   = mean_regridder.regrid(conc_OM.isel(time=1), like).where(raster==1)
conc_OM_1999   = mean_regridder.regrid(conc_OM.isel(time=2), like).where(raster==1)
conc_OM_2009   = mean_regridder.regrid(conc_OM.isel(time=3), like).where(raster==1)
conc_OM_2018   = mean_regridder.regrid(conc_OM.isel(time=4), like).where(raster==1)
conc_OM_re     = [conc_OM_1979, conc_OM_1989,conc_OM_1999,conc_OM_2009, conc_OM_2018]

depth_OM_ds = xr.Dataset()
for i in range(0,5):
    depth_OM_ds[i] = conc_meta["z"].where(conc_OM_re[i] < fresh_upper).where(raster==1).min("layer").mean().compute()
depth_OM_da = depth_OM_ds.to_array()    
#%% Process MM Data for study area
conc_meta_14 = conc_meta.isel(time=0, drop=True)
conc_meta_20 = conc_meta.isel(time=1, drop=True)
conc_meta_25 = conc_meta.isel(time=2, drop=True)
conc_meta_30 = conc_meta.isel(time=3, drop=True)
conc_meta_35 = conc_meta.isel(time=4, drop=True)
conc_meta_40 = conc_meta.isel(time=5, drop=True)
conc_meta_45 = conc_meta.isel(time=6, drop=True)
conc_meta_50 = conc_meta.isel(time=7, drop=True)

conc_meta_ar = [conc_meta_14, conc_meta_20, conc_meta_25,conc_meta_30,conc_meta_35,conc_meta_40,conc_meta_45,conc_meta_50]

depth_meta_ds = xr.Dataset()
for i in range(0,8):
    depth_meta_ds[i] = conc_OM["z"].where(conc_meta_ar[i]<fresh_upper).where(raster==1).min("layer").mean().compute()
depth_MM_da = depth_meta_ds.to_array()
# %% PLOTTING
times_OM = np.array(["1979", "1989", "1999", "2009", "2018"], dtype="datetime64")
times_MM = np.array(["1984", "1989", "1994", "1999", "2004", "2009", "2014", "2018"], dtype="datetime64") # not the actual times but for plotting

times_sim_OM = ["0", "10", "20", "30", "39"]
times_sim_MM = ["5", "10", "15", "20", "25", "30", "35", "39"]
# they only share the time dimension. Fix this
fig,ax = plt.subplots(sharex=True)
plt.plot(times_OM, depth_OM_da, color=(147/255, 187/255, 226/255))
plt.plot(times_MM, depth_MM_da, color=(35/255 , 130/255, 183/255))
plt.grid(axis="y")
#plt.title("Depth of fresh-saline interface over time")
plt.ylabel("depth [m]")
plt.ylim((-80,-50))
plt.xlabel("time [y]")
blu_patch     = mpatches.Patch(color=(147/255, 187/255, 226/255)  ,     label='Original Model')
orn_patch     = mpatches.Patch(color=(35/255 , 130/255, 183/255),     label='Metamodel ')
ax.legend(handles=[blu_patch, orn_patch],loc="lower right")
path = pathlib.Path(f"reports/images/depth-interface_OM_MM_cond1.png")
plt.savefig(path, dpi=200)

#%%
# MM
times_MM = ["2014", "2020", "2025", "2030", "2035", "2040", "2045","2050"]
fig,ax = plt.subplots()
plt.plot(times_MM, depth_MM_da)
plt.title("Depth of fresh-saline interface, MM")
plt.ylabel("depth [m]")
#%%

# %%
