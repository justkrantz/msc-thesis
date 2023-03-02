"""
- In this script, the cond of infiltration ponds will be calibrated. 
- The calibration will be done based on budgets (4.2)
- Perforiming a SS run of 1s to bring the budgets of OM and MM closer together
- After sucessful calibration, this cond can be used to study the effect
  on the fresh-saline interface depth in (4.5)
- Calibration steps:
    - cond1         = cond as calculated by 1.4 - based on OM budgets and heads.
    - cond2         = cond1/2
    - cond3         = cond1*0.75
    - cond4         = cond1*0.55
    - cond5         = cond1*0.65
    - cond6         = cond1*0.625
    - cond_final    = conductance as calibrated.  = cond6
- cond_final is used in (1.5-create-ghb)
"""
#%%
import imod
import numpy as np
import os
import xarray as xr
import matplotlib.pyplot as plt
os.chdir("c:/projects/msc-thesis")
# %% Data
# import
cond1_IP = xr.open_dataarray(r"data/2-interim/cond_250_inf_ponds.nc")
# Process 
cond2_IP = 0.5*cond1_IP
cond3_IP = 0.75*cond1_IP
cond4_IP = 0.65*cond1_IP
cond5_IP = 0.60*cond1_IP
cond6_IP = 0.625*cond1_IP

# %% Save data
cond2_IP.to_netcdf("data/2-interim/cond2_IP.nc")
cond3_IP.to_netcdf("data/2-interim/cond3_IP.nc")
cond4_IP.to_netcdf("data/2-interim/cond4_IP.nc")
cond5_IP.to_netcdf("data/2-interim/cond5_IP.nc")
cond6_IP.to_netcdf("data/2-interim/cond6_IP.nc")

# %%
