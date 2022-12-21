#%%
"""
Create:
- Basic Transport
- Dispersion
- AdvectionTVD
- Variable Density Flow
 
 *  This script uses the same input for starting concentrations as the original model,
    But regridded
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

# Open output data, to be used as input for future runs
c1_2054 = imod.idf.open(r"data\4-output\conc\conc_c1_205412312359_l*.IDF") # Cl
c2_2054 = imod.idf.open(r"data\4-output\conc\conc_c2_205412312359_l*.IDF") # AM
c3_2054 = imod.idf.open(r"data\4-output\conc\conc_c3_205412312359_l*.IDF") # Polders

# Use the same concentrations that are used by Dunea
conc_25m  = xr.open_zarr(r"data\1-external\data-25-run-1\conc-selection.zarr")["conc"].astype(np.float64)
c1_t0_25m = conc_25m.isel(time=0, drop=True)
c1_t0_25m = c1_t0_25m.swap_dims({"layer":"z"})
#%%
mean_regridder = imod.prepare.Regridder(method="mean")

#%%
chloride_coarse = mean_regridder.regrid(c1_t0_25m, like)
chloride_new    = chloride_coarse.where(ibound_coarse)
chloride_new    = chloride_new.assign_coords(layer=("z", np.arange(1,50)))

chloride_fresh  = chloride_new.notnull() * chloride_new.min()
chloride_saline = chloride_new.notnull() * chloride_new.max()

chloride = chloride_new

species_nd = xr.concat([
    chloride.assign_coords(species=1), #cl
    xr.full_like(chloride, 0.0).where(chloride.notnull()).assign_coords(species=2),  # AM
    xr.full_like(chloride, 0.0).where(chloride.notnull()).assign_coords(species=3)], # polders
    dim="species")
#%%

species_out = xr.concat([
    c1_2054.squeeze("time"),
    c2_2054.squeeze("time"),
    c3_2054.squeeze("time")],
    dim="species")
species_out = species_out.swap_dims({"layer":"z"}).drop("time")
# output contains a negative value, erase it?
#species_positive = species_out["c1"] > 0
#ds_negative = species_out["c1"] < 0
#species_out["c1"] = species_out["c1"].where(~ds_negative, other=0.0)


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
