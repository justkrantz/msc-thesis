# %%
"""
- Find the conductances for polders and infiltration ponds of MM, using data from riv OM 
    - Also calculate infiltration ponds conductance here using 25m data
    - Infiltration ponds conductance is saved also. 
        Note that conductance here is inconsistent with other infiltration ponds dataarrays["stage"] etc.
        The inf_ponds[cond] dataarray has a NaN where the other inf_ponds are active. fixed in 1.5
- To be used in 1.5-create-ghb
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
inf_ponds     = xr.open_dataset(r"data/1-external/infiltration_ponds.nc").mean("time", skipna = True)
ibound_coarse = xr.open_dataarray(r"data/2-interim/ibound_coarse.nc")

SH_25         = imod.idf.open(r"c:\projects\msc-thesis\DUNEA_1\3- input-dunea_transient\bas\starting_head_l*.idf").astype(np.float64)
H_SS_25       = xr.open_zarr(r"c:\projects\msc-thesis\DUNEA_1\4-output\head_ss_t0.zarr")["head"].astype(np.float64)

like = xr.open_dataarray("data/2-interim/like.nc").astype(np.float64)
# %% Regrid stage and budget
sum_regridder  = imod.prepare.Regridder(method="sum", use_relative_weights=True)
mean_regridder = imod.prepare.Regridder(method="mean")

# steady state heads from Dunea
cell_SS_25 =  H_SS_25.swap_dims({"layer":"z"}).drop("time")
H_SS_250       = mean_regridder.regrid(cell_SS_25, like)

# Polders
r_25_s = riv_25_stage.swap_dims({"layer": "z"})
r_25_b = riv_25_bdg_da.swap_dims({"layer": "z"})
cell_SS_25 =  H_SS_25.swap_dims({"layer":"z"}).drop("time")
riv_250_stage  = mean_regridder.regrid(r_25_s, like).mean("time")
riv_250_budget = sum_regridder.regrid(r_25_b,  like)

# Inf_ponds except conductance
inf_ponds_stage_re = mean_regridder.regrid(inf_ponds["stage"], like)

#%% Calculate cond using bdg and stage
# rivers conductance
h_cell_250 = H_SS_250.where(riv_25_cond.notnull().any())
cond_250   = riv_250_budget / (riv_250_stage - h_cell_250)

cond_250.to_netcdf("data/2-interim/cond_250_polders.nc")

# infiltration ponds conductance
h_cell_inf_ponds   = H_SS_250.where(inf_ponds["is_pond_2D"].notnull().any())
cond_250_inf_ponds = riv_250_budget / (inf_ponds_stage_re - h_cell_inf_ponds)
cond_250_ip_ib = cond_250_inf_ponds.where(ibound_coarse.notnull())

#cond_250_inf_ponds.to_netcdf("data/2-interim/cond_250_inf_ponds.nc")
cond_250_ip_ib.to_netcdf("data/2-interim/cond_250_inf_ponds.nc")


# %%
