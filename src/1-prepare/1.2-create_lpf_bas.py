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
# Open data
template     = xr.open_dataarray("data/1-external/template_2d.nc")
starting_head = xr.open_dataarray("data/1-external/starting-head.nc")
conductivity = xr.open_dataset("data/1-external/conductivity.nc")
like = xr.open_dataarray("data/2-interim/like.nc")

kh = conductivity["kh"]
kv = conductivity["kv"]

#%%
# preparing regridders
sum_regridder = imod.prepare.Regridder(method="sum", use_relative_weights=True)
mean_regridder = imod.prepare.Regridder(method="mean")
harmonic_regridder = imod.prepare.Regridder(method="harmonic_mean")

#%%
# ibound
domain2d = starting_head.isel(z=-1, drop =True).notnull()
ibound = kh.notnull() & domain2d

ibound_re = sum_regridder.regrid(ibound,like)
ibound_coarse = ibound_re > 50
ibound_coarse = (ibound_coarse
    .assign_coords(layer =("z", np.arange(1,50)))
    .assign_coords(dz=kh["dz"]).drop(["dx", "dy"])
    .assign_coords(dx=like["dx"], dy=like["dy"])
)
ibound_coarse_ds = ibound_coarse.to_dataset(name="ibound_coarse")
#ibound_coarse = ibound_coarse.assign_coords(dx=like["dx"],dy=like["dy"])

ibound_coarse_ds.to_netcdf("data/2-interim/ibound_coarse.nc") 
#%%
# Conductivity
kh_coarse = mean_regridder.regrid(kh,like)

kh_coarse = (kh_coarse
    .where(ibound_coarse)
    .assign_coords(layer=("z", np.arange(1, 50)))
    .assign_coords(dz=kh["dz"]).drop(["dx", "dy"])
)
kv_coarse = mean_regridder.regrid(kv,like)

kv_coarse = (kv_coarse
    .where(ibound_coarse)
    .assign_coords(layer=("z", np.arange(1, 50)))
    .assign_coords(dz=kh["dz"]).drop(["dx", "dy"])
)


#%%
# Starting head
SH_re = mean_regridder.regrid(starting_head, like)
SH_re = SH_re.where(ibound_coarse)

#%%
# Basic Flow
bas = imod.wq.BasicFlow(
    ibound = ibound_coarse,    #must be dataarray
    top    = ibound.coords["ztop"][0],
    bottom = ibound.coords["zbot"].zbot,
    starting_head = SH_re,
    inactive_head = -9999.0,
)
bas.dataset.to_netcdf("data/3-input/bas.nc")
#%%
# Layer Property Flow
lpf = imod.wq.LayerPropertyFlow(k_horizontal = kh_coarse, k_vertical = kv_coarse)
lpf.dataset.to_netcdf("data/3-input/lpf.nc")

# %%
