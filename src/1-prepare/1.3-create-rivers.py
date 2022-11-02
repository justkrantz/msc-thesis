# %% 

import os

import imod
import numpy as np
import scipy.ndimage
import xarray as xr

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

river_dataset = xr.open_dataset("data/1-external/river.nc")#.dropna("z", how="all")
like          = xr.open_dataarray("data/2-interim/like.nc")
inf_ponds     = xr.open_dataset("data/1-external/infiltration_ponds.nc").drop("is_pond_2D")
# %% process data

inf_ponds_mean = inf_ponds.mean("time", skipna=True)
riv_mean = river_dataset.mean("time")
river = riv_mean.combine_first(inf_ponds_mean)

#%%
# Remove "boezem" areas from the river stages

river_stage = river["stage"].max("z")
full_river  = imod.prepare.fill(river_stage)
moving_average_river = moving_average(full_river, 11)


# %%
# We use the moving average to detect the high elevation canals. However, this
# results in a a false positive near the dunes. This looks like the only false
# positive, so we force all locations above the line y=462_500 to be kept.

keep = (full_river - moving_average_river) < 1.0
keep = keep | (keep["y"] > 462_500.0)
filtered_river_dataset = river.where(keep)

# %%

mean_regridder = imod.prepare.Regridder(method="mean")
cond_regridder = imod.prepare.Regridder(method="conductance")

river_regridded = xr.Dataset()
for var in ("stage", "bot", "density"):
    river_regridded[var] = mean_regridder.regrid(filtered_river_dataset[var], like=like)
river_regridded["cond"] = cond_regridder.regrid(filtered_river_dataset["cond"], like=like)

# %%

river_regridded = river_regridded.assign_coords(layer=("z", np.arange(1, 50)))

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

# %%
