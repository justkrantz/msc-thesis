"""
Create river and infiltration ponds onjects
* Data imported
* Moving average for removing unwanted "boezem" effect
* Species added, to be used for replicating Stuyfzand's geochemical analyses
    conc      (chloride conc)       = Cl
    river     (Artificial Polder)   = AP
    inf_ponds (Artificial Meuse)    = AM

Notes
- River is also saved as a river package in this script, but currently unused
- It's saved as a netcdf in this script, which is used in 1.5-create-ghb
    
"""
# %% 
import os
import imod
import numpy as np
import scipy.ndimage
import xarray as xr
import numpy as np
# %%
os.chdir("c:/projects/msc-thesis")
# %%
# Read input data.
like          = xr.open_dataarray("data/2-interim/like.nc")
ibound_coarse = xr.open_dataset("data/2-interim/ibound_coarse.nc")
river         = xr.open_dataset("data/1-external/river.nc")
conc          = xr.open_dataarray("data/2-interim/chloride_coarse.nc")
# %% Functions
# moving average to remove boezems
def moving_average(da, windowsize: int):
    weights = np.ones((windowsize, windowsize))
    weights = weights / weights.sum()  # sums to 1
    out = da.copy()
    scipy.ndimage.convolve(da.values, weights, out.values)
    return out
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
# process data: find mean and filter "boezems" out
river_mean     = river.mean("time", skipna=True)
river_stage    = river_mean["stage"].max("z")
river_full     = imod.prepare.fill(river_stage)
moving_avg_riv = moving_average(river_full,11)

keep = (river_full - moving_avg_riv) < 1.0
keep = keep | (keep["y"] > 462_500.0)
filtered_riv_ds = river_mean.where(keep)
#%%
# Regridders
mean_regridder = imod.prepare.Regridder(method="mean")
cond_regridder = imod.prepare.Regridder(method="conductance")

river_regridded = xr.Dataset()
for var in ("stage", "cond", "bot", "density"):
    river_regridded[var] = mean_regridder.regrid(filtered_riv_ds[var], like=like)
# ink z and layers 
river_linked  = link_z_layer(river_regridded, ibound_coarse)
# %%
# Add concentration[species] dimension to river
y = ibound_coarse["y"]
x = ibound_coarse["x"]

cond = river_linked["cond"]

conc_polders = xr.full_like(cond, 0.0).where(cond.notnull()) # [Cl] = 0?
species_nd = xr.concat([
    conc_polders.assign_coords(species=1), #cl
    xr.full_like(conc_polders, 0.0).where(conc_polders.notnull()).assign_coords(species=2),  # AM
    xr.full_like(conc_polders, 1.0).where(conc_polders.notnull()).assign_coords(species=3)], # polders
    dim="species")

river_linked["conc"] = species_nd
river_linked.to_netcdf("data/2-interim/river.nc")
#%% UNUSED
#riv = imod.wq.River(stage               = river_linked["stage"],
#                    conductance         = river_linked["cond"],
#                    bottom_elevation    = river_linked["bot"],
#                    density             = river_linked["density"],
#                    concentration       = river_linked["conc"],
#                    save_budget         = True 
#)

# %%
