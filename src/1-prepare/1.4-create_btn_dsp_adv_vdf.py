#%%
"""
Create:
- Basic Transport
- Dispersion
- AdvectionTVD
- Variable Density Flow
"""
#%%
import numpy as np
import imod
import os
import xarray as xr
#%%
os.chdir("c:/projects/msc-thesis")
#%%
# Open data
ibound_coarse = xr.open_dataarray("data/2-interim/ibound_coarse.nc")
chloride  = xr.open_dataarray("data/1-external/chloride.nc")
like      = xr.open_dataarray("data/2-interim/like.nc")
inf_ponds = xr.open_dataset(r"data/1-external/infiltration_ponds.nc")
#%%
mean_regridder = imod.prepare.Regridder(method="mean")

#%%
chloride_coarse = mean_regridder.regrid(chloride, like)
chloride_new    = chloride_coarse.where(ibound_coarse)
chloride_new    = chloride_new.assign_coords(layer=("z", np.arange(1,50)))

chloride_fresh  = chloride_new.notnull() * chloride_new.min()
chloride_saline = chloride_new.notnull() * chloride_new.max()

chloride = chloride_saline

species_nd = xr.concat([
    chloride.assign_coords(species=1), #cl
    xr.full_like(chloride, 0.0).where(chloride.notnull()).assign_coords(species=2),  # AM
    xr.full_like(chloride, 0.0).where(chloride.notnull()).assign_coords(species=3)], # polders
    dim="species")

#%%
btn = imod.wq.BasicTransport(icbund=ibound_coarse, starting_concentration=species_nd, n_species=3)
dsp = imod.wq.Dispersion(longitudinal=0.001)
adv = imod.wq.AdvectionTVD(courant=1.0)
vdf = imod.wq.VariableDensityFlow(density_concentration_slope=0.71)

#%%
# Save datasets
chloride_coarse.to_netcdf("data/2-interim/chloride_coarse.nc")
btn.dataset.to_netcdf("data/3-input/btn.nc")
dsp.dataset.to_netcdf("data/3-input/dsp.nc")
adv.dataset.to_netcdf("data/3-input/adv.nc")
vdf.dataset.to_netcdf("data/3-input/vdf.nc")
# %%
