"""
- Create the constand head boudnary in a separate script
- Assign species to this boundary condition
"""
#%%

import imod
import os
import xarray as xr
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
#%%
os.chdir("c:/projects/msc-thesis")
#%%
# Open data
inf_ponds     = xr.open_dataset(r"data/1-external/infiltration_ponds.nc").drop("is_pond_2D")
ibound_coarse = xr.open_dataarray(r"data/2-interim/ibound_coarse.nc")
shead_coarse  = xr.open_dataarray(r"data/2-interim/starting-head-coarse.nc") 
#%%
# Functions
# Find the boundary of the lowest layer
def find_boundary(ibound):
    deepest_ibound = ibound.isel(z=-1, drop=True)
    eroded = deepest_ibound.copy(data=scipy.ndimage.binary_erosion(deepest_ibound.values))
    is_boundary = (deepest_ibound == 1) & (eroded == 0)
    return is_boundary

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
#%%
# Boundary 
boundary = find_boundary(ibound_coarse)
shead_bound = shead_coarse.isel(z=-1)
chloride = xr.full_like(shead_bound, 16.048)
species_nd = xr.concat([
    chloride.assign_coords(species=1), #cl
    xr.full_like(chloride, 0.0).where(chloride.notnull()).assign_coords(species=2),  # AM
    xr.full_like(chloride, 0.0).where(chloride.notnull()).assign_coords(species=3)], # polders
    dim="species")

ds_bound = xr.Dataset()
ds_bound["stage"]   = shead_bound
ds_bound["conc"]    = species_nd
ds_bound["cond"]    = xr.full_like(shead_bound, 5000.0)     # High value
ds_bound = ds_bound.expand_dims("z").where(boundary)        # may be needed to add again if error!

ds_linked = link_z_layer(ds_bound, ibound_coarse)

chd_out = imod.wq.ConstantHead(
    ds_linked["stage"], 
    ds_linked["stage"],
    ds_linked["conc"],
    )
chd_out.dataset.to_netcdf("data/3-input/chd.nc")
# %%
