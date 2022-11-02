#%%
import imod
import os
import pandas as pd
import xarray as xr
import scipy.ndimage
#%%
os.chdir("c:/projects/msc-thesis")
# %%

def find_boundary(ibound):
    deepest_ibound = ibound.isel(z=-1, drop=True)
    eroded = deepest_ibound.copy(data=scipy.ndimage.binary_erosion(deepest_ibound.values))
    is_boundary = (deepest_ibound == 1) & (eroded == 0)
    return is_boundary

# %%
# Open data

shead = xr.open_dataarray("data/1-external/starting-head.nc")
ghb = xr.open_dataset("data/1-external/generalheadboundary.nc")
like = xr.open_dataarray("data/2-interim/like.nc")
ibound_coarse = xr.open_dataarray("data/2-interim/ibound_coarse.nc")
coarse_chloride = xr.open_dataarray("data/2-interim/chloride_coarse.nc")
#ibound = xr.open_dataarray("data/2-interim/ibound.nc")
# %%
sea = xr.open_dataset("data/1-external/sea.nc")
ghb = ghb.combine_first(sea)

cond_regridder = imod.prepare.Regridder(method= "conductance")
mean_regridder = imod.prepare.Regridder(method= "mean")

ds = xr.Dataset()
for var in ("stage", "conc", "density"):
    ds[var] = mean_regridder.regrid(ghb[var], like=like)
ds["cond"] = cond_regridder.regrid(ghb["cond"], like=like)

# %%
shead_coarse = mean_regridder.regrid(shead,like)
is_boundary = find_boundary(ibound_coarse)
#%%

ghb_resistance = 1.0  # day
reference_density = 1000.0  
density_concentration_slope = 0.71 # kg / kg
surface_area = (ibound_coarse["dx"] * abs(ibound_coarse["dz"])) # to make positive

boundary_ds = xr.Dataset()
boundary_ds["stage"] = shead_coarse.where(is_boundary)
boundary_ds["conc"] = coarse_chloride.where(is_boundary)
boundary_ds["density"] = (reference_density + boundary_ds["conc"] * density_concentration_slope).where(is_boundary)
boundary_ds["cond"] = (surface_area / ghb_resistance).where(boundary_ds["stage"].notnull()).transpose("z", "y", "x")

ds = ds.combine_first(boundary_ds)

# %%
ghb_out = imod.wq.GeneralHeadBoundary(
    head=boundary_ds["stage"],
    conductance=boundary_ds["cond"],
    concentration=boundary_ds["conc"],
    density=boundary_ds["density"],
    save_budget= True
)
ghb_out.dataset.to_netcdf("data/3-input/ghb.nc")

# %%
