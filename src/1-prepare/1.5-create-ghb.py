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
inf_ponds     = xr.open_dataset("data/1-external/infiltration_ponds.nc").drop("is_pond_2D")

# %%
# Process data
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
# Add infiltration ponds
inf_ponds_mean      = inf_ponds.mean("time", skipna = True)
inf_ponds_regridded = xr.Dataset()
for var in ("stage" , "bot", "density"):
    inf_ponds_regridded[var] = mean_regridder.regrid(inf_ponds_mean[var], like=like)
inf_ponds_regridded["cond"] = cond_regridder.regrid(inf_ponds_mean["cond"], like=like)
#%%
# Add concentration of infiltration ponds

#Variable "stage" needs to be renamed to "concentration"
inf_ponds_conc = xr.zeros_like(inf_ponds_regridded["stage"]).where(inf_ponds_regridded["stage"].notnull())
inf_ponds_regridded["conc"] = inf_ponds_conc

#%%
# Combine the two a new dataset
ds_combined = xr.Dataset()
for var in ("stage", "cond", "conc", "density"):
    ds_combined[var] = inf_ponds_regridded[var].combine_first(ds_clipped[var])
#%%
# Add missing z coordinates
ds_combined_z = ds_combined["z"]#.values
ibound_z = ibound_coarse["z"]#.values
layer = np.flatnonzero(np.isin(ibound_z, ds_combined_z)) + 1
ds_combined = ds_combined.assign_coords(layer=("z", layer))

# Add missing dz
# %%
# Note that the combine_first flips the layers! following line is necessary
flipped_ds = ds_combined.sel(z=slice(None, None, -1))

# Huite invention: to link z and layers correctly
ds_z = flipped_ds["z"]#.values
ibound_z = ibound_coarse["z"]#.values
layer = np.flatnonzero(np.isin(ibound_z, ds_z)) + 1

ds_final = (flipped_ds
    .assign_coords(layer=("z", layer))
    .assign_coords(dz = ibound_coarse["dz"])
    .assign_coords(zbot = ibound_coarse["zbot"])
    .assign_coords(ztop = ibound_coarse["ztop"])
)
# %%
ghb_out = imod.wq.GeneralHeadBoundary(
    head=ds_final["stage"],
    conductance=ds_final["cond"],
    concentration=ds_final["conc"],
    density=ds_final["density"],
    save_budget= True
)
ghb_out.dataset.to_netcdf("data/3-input/ghb.nc")

# %%
