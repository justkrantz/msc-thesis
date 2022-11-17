"""
Create river and infiltration ponds onjects
* Data imported
* Moving average for removing unwanted "boezem" effect
* Species added, to be used for replicating Stuyfzand's geochemical analyses
    conc      (chloride conc)       = Cl
    river     (Artificial Polder)   = AP
    inf_ponds (Artificial Meuse)    = AM

Notes
- River is also saved as a river package in this script, but currently unused,
    as it is added to the GHB package.
    
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

# %%
