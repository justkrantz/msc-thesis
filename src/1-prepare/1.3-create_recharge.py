#%%
""" 
Create recharge package after regridding. expand concentration dimension with species
"""
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
recharge      = xr.open_dataarray("data/1-external/recharge.nc")
like          = xr.open_dataarray("data/2-interim/like.nc")
ibound_coarse = xr.open_dataarray("data/2-interim/ibound_coarse.nc") 

#%%
# prepare regridders
mean_regridder = imod.prepare.Regridder(method = "mean")

#%%
# Regrid recharge
recharge_coarse  = mean_regridder.regrid(recharge,like)
recharge_mean    = recharge_coarse.mean("layer").mean("time") # recharge on inactieve cells maakt niet uit
#%%
# expand concentration dimension into species dimension
y = ibound_coarse["y"]
x = ibound_coarse["x"]
cond = recharge_mean

conc = xr.full_like(cond, 0.0).where(cond.notnull()) # [Cl] = 0?
species_nd = xr.concat([
    conc.assign_coords(species=1),  # cl
    xr.full_like(conc, 0.0).where(conc.notnull()).assign_coords(species=2),  # AM
    xr.full_like(conc, 0.0).where(conc.notnull()).assign_coords(species=3)], # polders
    dim="species")

 #%%
rch =  imod.wq.RechargeHighestActive(rate=recharge_mean, concentration=species_nd, save_budget=True)
rch.dataset.to_netcdf("data/3-input/rch.nc")

# %%
