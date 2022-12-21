"""
Create the content of the LPF and BAS packages.

Steps in this script:

* Read 25 m data
* Regrid IBOUND data to 250 m: Only make 250 m cells active if more than half of
  volume is occupied by 25 m active cells
* Regrid conductivity parameters...
* Set up BasicFlow model
* Set up LayerPropertyFlow model

For the starting heads
* Heads calculated by the 25m model are used (SS run)
* Heads from output of previous run can be used
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
# Open data
template      = xr.open_dataarray("data/1-external/template_2d.nc")
starting_head = xr.open_zarr(r"data\1-external\data-25-run-1\head_ss_t0.zarr")
starting_head_ar = starting_head["head"].astype(np.float64)
#starting_head_2 = starting_head_ar.to_netcdf()
starting_head_3 = starting_head_ar.swap_dims({"layer":"z"}).drop("time")
starting_head_nc = xr.open_dataarray("data/1-external/starting-head.nc")
conductivity  = xr.open_dataset("data/1-external/conductivity.nc")
like = xr.open_dataarray("data/2-interim/like.nc")

kh = conductivity["kh"]
kv = conductivity["kv"]

#%%
# preparing regridders
sum_regridder      = imod.prepare.Regridder(method="sum", use_relative_weights=True)
mean_regridder     = imod.prepare.Regridder(method="mean")
harmonic_regridder = imod.prepare.Regridder(method="harmonic_mean")
#%%
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

#%%

# ibound
domain2d = starting_head_nc.isel(z=-1, drop =True).notnull()
ibound = kh.notnull() & domain2d

ibound_re = sum_regridder.regrid(ibound,like)
ibound_coarse = ibound_re > 50
ibound_coarse = (ibound_coarse
    .assign_coords(layer =("z", np.arange(1,50)))
    .assign_coords(dz=kh["dz"]).drop(["dx", "dy"])
    .assign_coords(dx=like["dx"], dy=like["dy"])
)

ibound_coarse_ds = ibound_coarse.to_dataset(name="ibound_coarse")
ibound_coarse_ds.to_netcdf("data/2-interim/ibound_coarse.nc") 
#%%
# Conductivity
kh_coarse = mean_regridder.regrid(kh,like)

kh_coarse = (kh_coarse
    .where(ibound_coarse)
    .assign_coords(layer=("z", np.arange(1, 50)))
    .assign_coords(dz=kh["dz"]).drop(["dx", "dy"])
)
kv_coarse = harmonic_regridder.regrid(kv,like)

kv_coarse = (kv_coarse
    .where(ibound_coarse)
    .assign_coords(layer=("z", np.arange(1, 50)))
    .assign_coords(dz=kh["dz"]).drop(["dx", "dy"])
)

#%%
# Starting head

SH_re = mean_regridder.regrid(starting_head_3, like)
SH_re = SH_re.where(ibound_coarse)
#SH_re_2 = link_z_layer(SH_re,ibound_coarse)
SH_re.to_netcdf(r"data/2-interim/starting-head-coarse.nc")

#%%
# Basic Flow
bas = imod.wq.BasicFlow(
    ibound = ibound_coarse,    #must be dataarray
    top    = ibound.coords["ztop"][0],
    bottom = ibound.coords["zbot"].zbot,
    starting_head = SH_re,
    inactive_head = -9999.0
)
bas.dataset.to_netcdf("data/3-input/bas.nc")
#%%
# Layer Property Flow
lpf = imod.wq.LayerPropertyFlow(k_horizontal = kh_coarse, k_vertical = kv_coarse,save_budget = True)
lpf.dataset.to_netcdf("data/3-input/lpf.nc")

# %%
