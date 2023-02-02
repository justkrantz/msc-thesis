"""
In this script the depth of the fresh-saline interface will be plotted over time for the study area, various scenarios
 - the idea is to come to an understanding of the artificial infiltration in the dune area,
    specifically the how much time it takes for freshwater to infiltrate  to a certain depth.
-  The scenarios include: 
    1. Starting conc as in OM, for callibration purpose
    2. Starting conc fully saline
    3. Starting conc in SA as fully saline (to mimic Stuyfzand)
  
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
raster        = imod.prepare.rasterize(gdf, like) 
# Bounds for groundwater types
fresh_upper = 0.150   # g/l
brack_upper = 8.0000  # g/l
    
#%% Process data OM
conc_OM_1979   = mean_regridder.regrid(conc_OM.isel(time=0), like).where(raster==1)
conc_OM_1989   = mean_regridder.regrid(conc_OM.isel(time=1), like).where(raster==1)
conc_OM_1999   = mean_regridder.regrid(conc_OM.isel(time=2), like).where(raster==1)
conc_OM_2009   = mean_regridder.regrid(conc_OM.isel(time=3), like).where(raster==1)
conc_OM_2018   = mean_regridder.regrid(conc_OM.isel(time=4), like).where(raster==1)

conc_OM_re = [conc_OM_1979,conc_OM_1989,conc_OM_1999,conc_OM_2009, conc_OM_2018]

depth_OM_ds = xr.Dataset()
fig,ax = plt.subplots()
for i in range(0,4):
    depth_OM_ds[i] = conc_meta["z"].where(conc_OM_re[i] < fresh_upper).where(raster==1).min("layer").mean().compute()

depth_OM_da = depth_OM_ds.to_array()    

#%%

# Meta
conc_meta_14 = conc_meta.isel(time=0, drop=True)
conc_meta_20 = conc_meta.isel(time=1, drop=True)
conc_meta_25 = conc_meta.isel(time=2, drop=True)
conc_meta_30 = conc_meta.isel(time=3, drop=True)
conc_meta_35 = conc_meta.isel(time=4, drop=True)
conc_meta_40 = conc_meta.isel(time=5, drop=True)
conc_meta_45 = conc_meta.isel(time=6, drop=True)
conc_meta_50 = conc_meta.isel(time=7, drop=True)
conc_meta_54 = conc_meta.isel(time=8, drop=True) 


raster        = imod.prepare.rasterize(gdf, like) 
#%% Depth of fresh-brackish interface   
# Bounds for groundwater types
fresh_upper = 0.150   # g/l
brack_upper = 8.0000  # g/l

# Depth fresh-saline interface
depth_fresh_meta2  = conc_meta["z"].where(conc_meta_39y < fresh_upper).min("layer")   # is this correct?
depth_fresh_meta_H = depth_fresh_meta2.combine_first(surface_level) 

depth_fresh_meta2  = conc_meta["z"].where(conc_meta_39y < fresh_upper).min("layer")   # is this correct?
depth_fresh_meta_H = depth_fresh_meta2.combine_first(surface_level) 




# %%
