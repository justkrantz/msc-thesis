# %%
"""
Find the conductances for polder area in the 250m model, using data from riv 25m model To be used in 1.5-create-ghb
"""
#%%
import imod
import numpy as np
import os
import xarray as xr
import matplotlib.pyplot as plt
#%%
os.chdir("c:/projects/msc-thesis")
#%%
# Open input data 25m model
riv_25_stage  = imod.idf.open(r"c:\projects\msc-thesis\DUNEA_1\3- input-dunea_transient\riv\stage_19791231235959_l*.idf") # First date is 1s before next, is the mean
riv_25_budget = xr.open_zarr(r"DUNEA_1\4-output\bdgriv_ss_t0.zarr") # budget file is SS
riv_25_bdg_da = riv_25_budget["bdgriv"]
riv_25_cond   = imod.idf.open(r"c:\projects\msc-thesis\DUNEA_1\3- input-dunea_transient\riv\conductance_l*.idf").astype(np.float64)

SH_25         = imod.idf.open(r"c:\projects\msc-thesis\DUNEA_1\3- input-dunea_transient\bas\starting_head_l*.idf").astype(np.float64)
H_SS_25       = xr.open_zarr(r"c:\projects\msc-thesis\DUNEA_1\4-output\head_ss_t0.zarr")["head"].astype(np.float64)

like = xr.open_dataarray("data/2-interim/like.nc").astype(np.float64)
# %%
# Regrid stage and budget
sum_regridder  = imod.prepare.Regridder(method="sum", use_relative_weights=True)
mean_regridder = imod.prepare.Regridder(method="mean")

r_25_s = riv_25_stage.swap_dims({"layer": "z"})
r_25_b = riv_25_bdg_da.swap_dims({"layer": "z"})

cell_SS_25 =  H_SS_25.swap_dims({"layer":"z"}).drop("time")

riv_250_stage  = mean_regridder.regrid(r_25_s, like)
riv_250_budget = sum_regridder.regrid(r_25_b, like)
H_SS_250       = mean_regridder.regrid(cell_SS_25, like)

#%% Method to calculate cond using bdg and stage
h_cell_250 = H_SS_250.where(riv_25_cond.notnull().any())
cond_250   = riv_250_budget / (riv_250_stage - h_cell_250)
cond_250   = cond_250.isel(time=0, drop = True)
cond_250.to_netcdf("data/2-interim/cond_250_polders.nc")
#%%
# Check: is cond25 using this method equal to cond 25 as input?
h_cell  = H_SS_25.where(riv_25_cond.notnull().any())
cond_25 = riv_25_bdg_da / (riv_25_stage - h_cell)

# %% Huite's kladblok
cond_25.isel(layer=4, time=0).plot.imshow(levels=np.arange(0.0, 310.0, 10.0), cmap="turbo")

riv_25_cond.isel(layer=4).plot.imshow(levels=np.arange(0.0, 310.0, 10.0), cmap="turbo")

diff = cond_25.isel(layer=4, time=0) - riv_25_cond.isel(layer=4)
reldiff = diff / riv_25_cond.isel(layer=4)

abs(reldiff).plot.imshow(levels=np.arange(0.0, 1.1, 0.1))

imod.rasterio.save("relative-diff.tif", abs(reldiff))

dh = abs(riv_25_stage - h_cell)
imod.rasterio.save("dh.tif", dh.isel(layer=4, time=0))

# %%
