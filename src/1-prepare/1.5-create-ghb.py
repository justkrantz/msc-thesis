#%%
"""
Create General Head Boundary package GHB as a combination of:
- infiltration ponds (from 1.3)
- river (from 1.3)
- sea 
"""
#%%
import imod
import os
import pandas as pd
import xarray as xr
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
#%%
os.chdir("c:/projects/msc-thesis")
# %%
# Open data
shead         = xr.open_dataarray(r"data/1-external/starting-head.nc")
like          = xr.open_dataarray(r"data/2-interim/like.nc")
ibound_coarse = xr.open_dataarray(r"data/2-interim/ibound_coarse.nc")
inf_ponds     = xr.open_dataset(r"data/1-external/infiltration_ponds.nc").drop("is_pond_2D")
shead_coarse  = xr.open_dataarray(r"data/2-interim/starting-head-coarse.nc") 
rivers        = xr.open_dataset(r"data/2-interim/river.nc")
sea           = xr.open_dataset(r"data/1-external/sea.nc")

# Robust method for linking z, dz and layer
def link_z_layer(ds, ibound):
    z = ibound["z"].values
    dz =ibound["dz"].values
    layer = ibound["layer"].values
    lookup1 = {key: value for key, value in zip(z, layer)}
    lookup2 = {key: value for key, value in zip(z, dz)}
    layer_numbers   = [lookup1[z] for z in ds["z"].values]
    layer_thickness = [lookup2[dz] for dz in ds["z"].values]
    return ds.assign_coords(layer=("z", layer_numbers),dz = ("z", layer_thickness))
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
ds_clipped["conc"] = ds_clipped["conc"]

#%%
# Infiltration ponds
inf_ponds_mean      = inf_ponds.mean("time", skipna = True)
inf_ponds_regridded = xr.Dataset()
for var in ("stage" , "bot", "density"):
    inf_ponds_regridded[var] = mean_regridder.regrid(inf_ponds_mean[var], like=like)
inf_ponds_regridded["cond"] = cond_regridder.regrid(inf_ponds_mean["cond"], like=like)
#%%
# Add concentration[species] dimension
# infiltration ponds 
y = ibound_coarse["y"]
x = ibound_coarse["x"]
cond = inf_ponds_regridded["cond"]

conc = xr.full_like(cond, 0.0).where(cond.notnull()) # [Cl] = 0?
species_nd = xr.concat([
    conc,  #Cl
    xr.full_like(conc, 1.0).where(conc.notnull()),  # AM
    xr.full_like(conc, 0.0).where(conc.notnull())], # polders
    dim="species")
inf_ponds_regridded["conc"]  = species_nd

# Sea
conc_sea = ds_clipped["conc"]
species_sea = xr.concat([
    conc_sea.assign_coords(species=1),  # Cl
    xr.full_like(conc_sea, 0.0).where(conc_sea.notnull()).assign_coords(species=2),  # AM
    xr.full_like(conc_sea, 0.0).where(conc_sea.notnull()).assign_coords(species=3)], # polders
    dim="species")
ds_sea_final = ds_clipped
ds_sea_final["conc"] = species_sea
ds_sea_final.to_netcdf("data/2-interim/sea.nc")
#%%
# Combine inf ponds and sea to a new dataset
ds_combined = xr.Dataset()
for var in ("stage", "cond", "conc", "density"):
    ds_combined[var] = inf_ponds_regridded[var].combine_first(ds_sea_final[var])

# combine with rivers
ds_comb_3 = xr.Dataset()
for var in ("stage", "cond", "conc", "density"):
    ds_comb_3[var] = ds_combined[var].combine_first(rivers[var])
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
