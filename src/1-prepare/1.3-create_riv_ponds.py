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

def moving_average(da, windowsize: int):
    weights = np.ones((windowsize, windowsize))
    weights = weights / weights.sum()  # sums to 1
    out = da.copy()
    scipy.ndimage.convolve(da.values, weights, out.values)
    return out



# %%
# Read input data.
like          = xr.open_dataarray("data/2-interim/like.nc")
inf_ponds     = xr.open_dataset("data/1-external/infiltration_ponds.nc").drop("is_pond_2D")
ibound_coarse = xr.open_dataset("data/2-interim/ibound_coarse.nc")

# %% 
# process data
inf_ponds_mean  = inf_ponds.mean("time", skipna=True)
#empty3d         = ibound_coarse.where(ibound_coarse, np.nan)

#%%
# Regridders
mean_regridder = imod.prepare.Regridder(method="mean")
cond_regridder = imod.prepare.Regridder(method="conductance")


river_regridded = xr.Dataset()
river_regridded["stage"] = mean_regridder.regrid(inf_ponds_mean["stage"], like=like)
river_regridded["cond"] = cond_regridder.regrid(inf_ponds_mean["cond"], like=like)
river_regridded["bot"] = mean_regridder.regrid(inf_ponds_mean["bot"], like=like)
river_regridded["density"] = mean_regridder.regrid(inf_ponds_mean["density"], like=like)

# %%
# Huite invention: to link z and layers correctly
river_z = river_regridded["z"]#.values
ibound_z = ibound_coarse["z"]#.values
layer = np.flatnonzero(np.isin(ibound_z, river_z)) + 1
river_regridded = river_regridded.assign_coords(layer=("z", layer))

#%%
riv = imod.wq.River(stage               = river_regridded["stage"],
                    conductance         = river_regridded["cond"],
                    bottom_elevation    = river_regridded["bot"],
                    density             = river_regridded["density"],
                    save_budget         = True 
)


# %%
# Store regridded result in a file.

riv.dataset.to_netcdf("data/3-input/river.nc")

