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
ibound_coarse = xr.open_dataset("data/2-interim/ibound_coarse.nc")
river         = xr.open_dataset("data/1-external/river.nc")       
# %% 
# process data
river_mean  = river.mean("time", skipna=True)

#%%
# Regridders
mean_regridder = imod.prepare.Regridder(method="mean")
cond_regridder = imod.prepare.Regridder(method="conductance")


river_regridded = xr.Dataset()
for var in ("stage", "cond", "bot", "density"):
    river_regridded[var] = mean_regridder.regrid(river_mean[var], like=like)

# %%
# Huite invention: to link z and layers correctly
river_z = river_regridded["z"]#.values
ibound_z = ibound_coarse["z"]#.values
layer = np.flatnonzero(np.isin(ibound_z, river_z)) + 1
river_regridded = river_regridded.assign_coords(layer=("z", layer))
river_regridded.to_netcdf("data/2-interim/river.nc")
#%%
riv = imod.wq.River(stage               = river_regridded["stage"],
                    conductance         = river_regridded["cond"],
                    bottom_elevation    = river_regridded["bot"],
                    density             = river_regridded["density"],
                    save_budget         = True 
)
