#%%
"""
Create Drainage and Well package
    Drainage:
    - Surface runoff defined by top of active cells in ibound, excluding the sea area.
    Well: 
    - Only exfiltration wells are used.  
    - Their average discharge is calculated and applied for all timesteps
"""
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
# Functions
def moving_average(da, windowsize: int):
    weights = np.ones((windowsize, windowsize))
    weights = weights / weights.sum()  # sums to 1
    out = da.copy()
    scipy.ndimage.convolve(da.values, weights, out.values)
    return out


# %%
# Open data
ibound_coarse = xr.open_dataarray("data/2-interim/ibound_coarse.nc") # opening as data array to store
ghb           = xr.open_dataset("data/3-input/ghb.nc")
well          = pd.read_csv("data/1-external/wells.csv") 
river_dataset = xr.open_dataset("data/1-external/river.nc")
like          = xr.open_dataarray("data/2-interim/like.nc")
sea           = xr.open_dataset(r"data/2-interim/sea_clipped.nc")
#%%
# Add rivers from river dataset and remove "boezems"
riv_mean = river_dataset.mean("time")

river_stage = riv_mean["stage"].max("z")
full_river  = imod.prepare.fill(river_stage)
moving_average_river = moving_average(full_river, 11)

# We use the moving average to detect the high elevation canals. However, this
# results in a a false positive near the dunes. This looks like the only false
# positive, so we force all locations above the line y=462_500 to be kept.

keep = (full_river - moving_average_river) < 1.0
keep = keep | (keep["y"] > 462_500.0)
filtered_river_dataset = riv_mean.where(keep)

#%%
# Prepare regridders
mean_regridder = imod.prepare.Regridder(method="mean")
cond_regridder = imod.prepare.Regridder(method="conductance")

river_regridded = xr.Dataset()
for var in ("stage", "bot", "density"):
    river_regridded[var] = mean_regridder.regrid(filtered_river_dataset[var], like=like)
river_regridded["cond"] = cond_regridder.regrid(filtered_river_dataset["cond"], like=like)

#%%
# Set up DRN: Elevation of surface runoff
top     = ibound_coarse.coords["ztop"]
top_layers = top.where(ibound_coarse != 0).min("z")

# exclude sea
sea_2d  = sea["stage"].isel(z=0, drop = True)

top3d   = top.where(ibound_coarse != 0 )
top3d_2 = top3d.where(sea_2d.isnull())

surface_level = top3d.max("z")
is_top = top3d == surface_level

surface_level_2 = top3d_2.max("z")
is_top_2 = top3d_2 == surface_level_2

drain_elevation_2 = top3d_2.where(is_top_2)

# Set up DRN: add river stage and conductance
# Without sea
drn_el_combined_2 = drain_elevation_2.combine_first(river_regridded["stage"])


#%%
# Conductance of drain

is_cond = is_top * ghb.conductance.max()
is_cond_2 = is_cond.where(is_top)

is_cond_lower = is_top * 250
is_cond_2_lower = is_cond_lower.where(is_top)

# conductance river drains
is_cond_combined = is_cond_2_lower.combine_first(river_regridded["cond"])
is_cond_no_sea   = is_cond_combined.where(sea_2d.isnull())

#%%
drn = imod.wq.Drainage(drn_el_combined_2, is_cond_no_sea, save_budget=True)

drn.dataset.to_netcdf("data/3-input/drn.nc")
#%%
# Wells
wells_2014 = well[well["time"] == "2014-12-31 23:59:59"]
wel = imod.wq.Well(
    id_name=wells_2014["idcode"],
    x=wells_2014["x"],
    y=wells_2014["y"],
    rate=wells_2014["rate"].min(),
    layer=wells_2014["layer"],
    save_budget=True,
)
wel.dataset.to_netcdf("data/3-input/wel.nc")

# %%
