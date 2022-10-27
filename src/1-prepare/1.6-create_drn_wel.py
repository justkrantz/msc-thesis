#%%
import scipy.ndimage
import imod
import numpy as np
import os
import pandas as pd
import xarray as xr
#%%
os.chdir("c:/projects/msc-thesis")

# %%
# Open data
ibound_coarse = xr.open_dataarray("data/2-interim/ibound_coarse.nc") # opening as data array to store
ghb           = xr.open_dataset("data/3-input/ghb.nc")
well          = pd.read_csv("data/1-external/wells.csv") 
#%%
# Drainage elevation of surface runoff
top     = ibound_coarse.coords["ztop"]
top_layers = top.where(ibound_coarse != 0).min("z")

top3d = top.where(ibound_coarse != 0)
surface_level = top3d.max("z")
is_top = top3d == surface_level

drain_elevation = top3d.where(is_top)
#%%
# Conductance of drain

is_cond = is_top * ghb.conductance.max()
is_cond_2 = is_cond.where(is_top)

is_cond_lower = is_top * 250
is_cond_2_lower = is_cond_lower.where(is_top)

drn = imod.wq.Drainage(drain_elevation, is_cond_2_lower, save_budget=True)
#%%
drn.dataset.to_netcdf("data/3-input/drn.nc")
#%%
# Wells
wells_2014 = well[well["time"] == "2014-12-31 23:59:59"]
wel = imod.wq.Well(
    id_name=wells_2014["idcode"],
    x=wells_2014["x"],
    y=wells_2014["y"],
    rate=wells_2014["rate"].min(),
    layer=wells_2014["layer"],
    save_budget=True,
)
wel.dataset.to_netcdf("data/3-input/wel.nc")

# %%
