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
recharge = xr.open_dataarray("data/1-external/recharge.nc")
like     = xr.open_dataarray("data/2-interim/like.nc")

#%%
# prepare regridders
mean_regridder = imod.prepare.Regridder(method = "mean")

#%%
# Regrid recharge
recharge_coarse  = mean_regridder.regrid(recharge,like)
recharge_mean    = recharge_coarse.mean("layer").mean("time") # recharge on inactieve cells maakt niet uit
 #%%
rch =  imod.wq.RechargeHighestActive(rate=recharge_mean, concentration=0.0, save_budget=True)
rch.dataset.to_netcdf("data/3-input/rch.nc")

# %%
