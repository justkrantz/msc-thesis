#%%
import imod
import os
import pandas as pd
import xarray as xr
import numpy as np
#%%
os.chdir("c:/projects/msc-thesis")
# %%
# Open data

shead = xr.open_dataarray("data/1-external/starting-head.nc")
like = xr.open_dataarray("data/2-interim/like.nc")
ibound_coarse = xr.open_dataarray("data/2-interim/ibound_coarse.nc")

#ibound = xr.open_dataarray("data/2-interim/ibound.nc")
# %%
sea = xr.open_dataset("data/1-external/sea.nc")


cond_regridder = imod.prepare.Regridder(method= "conductance")
mean_regridder = imod.prepare.Regridder(method= "mean")

ds = xr.Dataset()
for var in ("stage", "conc", "density"):
    ds[var] = mean_regridder.regrid(sea[var], like=like)
ds["cond"] = cond_regridder.regrid(sea["cond"], like=like)

ds_clipped = xr.Dataset()
for var in ("stage", "conc", "density", "cond"):
    ds_clipped[var] = ds[var].where(ibound_coarse)

#%%

# Huite invention: to link z and layers correctly
ds_z = ds_clipped["z"]#.values
ibound_z = ibound_coarse["z"]#.values
layer = np.flatnonzero(np.isin(ibound_z, ds_z)) + 1
ds_clipped = ds_clipped.assign_coords(layer=("z", layer))


# %%
ghb_out = imod.wq.GeneralHeadBoundary(
    head=ds_clipped["stage"],
    conductance=ds_clipped["cond"],
    concentration=ds_clipped["conc"],
    density=ds_clipped["density"],
    save_budget= True
)
ghb_out.dataset.to_netcdf("data/3-input/ghb.nc")

# %%
