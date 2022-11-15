#%%
import imod
import os
import pandas as pd
import xarray as xr
import numpy as np
import scipy.ndimage
#%%
os.chdir("c:/projects/msc-thesis")
# %%
# Open data
shead = xr.open_dataarray(r"data/1-external/starting-head.nc")
like = xr.open_dataarray(r"data/2-interim/like.nc")
ibound_coarse = xr.open_dataarray(r"data/2-interim/ibound_coarse.nc")
inf_ponds     = xr.open_dataset(r"data/1-external/infiltration_ponds.nc").drop("is_pond_2D")
shead_coarse  = xr.open_dataarray(r"data/2-interim/starting-head-coarse.nc") 
rivers  = xr.open_dataset(r"data/2-interim/river.nc")
sea = xr.open_dataset(r"data/1-external/sea.nc")
#%% to find the outer boundary, lowest layer
def find_boundary(ibound):
    deepest_ibound = ibound.isel(z=-1, drop=True)
    eroded = deepest_ibound.copy(data=scipy.ndimage.binary_erosion(deepest_ibound.values))
    is_boundary = (deepest_ibound == 1) & (eroded == 0)
    return is_boundary

# Robust method for linking z and layer
def link_z_layer(ds, ibound):
    z = ibound["z"].values
    layer = ibound["layer"].values
    lookup = {key: value for key, value in zip(z, layer)}
    layer_numbers = [lookup[z] for z in ds["z"].values]
    return ds.assign_coords(layer=("z", layer_numbers))
# %%
# Sea
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
# Infiltration ponds
inf_ponds_mean      = inf_ponds.mean("time", skipna = True)
inf_ponds_regridded = xr.Dataset()
for var in ("stage" , "bot", "density"):
    inf_ponds_regridded[var] = mean_regridder.regrid(inf_ponds_mean[var], like=like)
inf_ponds_regridded["cond"] = cond_regridder.regrid(inf_ponds_mean["cond"], like=like)
# Add concentration of infiltration ponds
inf_ponds_conc = xr.zeros_like(inf_ponds_regridded["stage"]).where(inf_ponds_regridded["stage"].notnull())
inf_ponds_regridded["conc"] = inf_ponds_conc
#%%
# Rivers
rivers["conc"] = xr.full_like(rivers["stage"], 16.048).where(rivers["stage"].notnull())
#%%
# Add ghb at bottom boundary
boundary = find_boundary(ibound_coarse)
shead_bound = shead_coarse.isel(z=-1)
ds_bound = xr.Dataset()
ds_bound["stage"]   = shead_bound
ds_bound["conc"]    = xr.full_like(shead_bound, 16.048)
ds_bound["density"] = 0.71*ds_bound["conc"] + 1000          # See vdf in scr1.4
ds_bound["cond"]    = xr.full_like(shead_bound, 5000.0)     # High value
ds_bound = ds_bound.expand_dims("z").where(boundary)        # may be needed to add again if error!
#%%
# Combine inf ponds and sea to a new dataset
ds_combined = xr.Dataset()
for var in ("stage", "cond", "conc", "density"):
    ds_combined[var] = inf_ponds_regridded[var].combine_first(ds_clipped[var])

# combine combined with shead_bound
ds_comb_2 = xr.Dataset()
for var in ("stage", "cond", "conc", "density"):
    ds_comb_2[var] = ds_combined[var].combine_first(ds_bound[var])

# combine with rivers
ds_comb_3 = xr.Dataset()
for var in ("stage", "cond", "conc", "density"):
    ds_comb_3[var] = ds_comb_2[var].combine_first(rivers[var])
# %%
ds_final = link_z_layer(ds_comb_3, ibound_coarse)
# %%
ghb_out = imod.wq.GeneralHeadBoundary(
    head          = ds_final["stage"],
    conductance   = ds_final["cond"],
    concentration = ds_final["conc"],
    density       = ds_final["density"],
    save_budget   = True
)
ghb_out.dataset.to_netcdf("data/3-input/ghb.nc")

# %%
