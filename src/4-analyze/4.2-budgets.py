""""
Analyze the budgets of the metamodel, compare with 25m heads:
- 25m budgets:
    - bdg drn
    - bdg riv
    - bdg wel

"""
#%%
import numpy as np
import os
import imod
import xarray as xr
import matplotlib.pyplot as plt
import scipy.ndimage.morphology
import pandas as pd
import pathlib
import geopandas
#%%
os.chdir("c:/projects/msc-thesis")
#%% 
sum_regridder = imod.prepare.Regridder(method="sum") 
mean_regridder = imod.prepare.Regridder(method="mean") 
# Import data
like         = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
gdf          = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
inf_ponds    = xr.open_dataset(r"c:\projects\msc-thesis\data\1-external\infiltration_ponds.nc")
inf_ponds = inf_ponds.isel(time=0, drop=True)

# Output: budgets from metamodel 
meta_drn_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgdrn\bdgdrn_205312312359_l*.idf").isel(time=0, drop=True)
meta_drn_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgdrn\bdgdrn_202412312359_l*.idf").isel(time=0, drop=True)

meta_ghb_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgghb\bdgghb_205312312359_l*.idf").isel(time=0, drop=True)
meta_ghb_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgghb\bdgghb_202412312359_l*.idf").isel(time=0, drop=True)

meta_rch_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgrch\bdgrch_205312312359_l*.idf").isel(time=0, drop=True)
meta_rch_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgrch\bdgrch_202412312359_l*.idf").isel(time=0, drop=True)

meta_wel_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgwel\bdgwel_205312312359_l*.idf").isel(time=0, drop=True)
meta_wel_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgwel\bdgwel_202412312359_l*.idf").isel(time=0, drop=True)

#meta_bnd_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgbnd\bdgbnd_205312312359_l*.idf").isel(time=0, drop=True)
#meta_bnd_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgbnd\bdgbnd_202412312359_l*.idf").isel(time=0, drop=True)

OM_drn = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\bdgdrn_ss_t0.zarr")["bdgdrn"]
OM_riv = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\bdgriv_ss_t0.zarr")["bdgriv"]
OM_wel = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\bdgwel_ss_t0.zarr")["bdgwel"]
# %% error
def er(expected, actual):
    re = actual - expected
    return re
# Relative error
def rel_er(expected, actual):
    re = np.abs((actual - expected) / expected)
    return re
# %% Process data
# OM - regrid
OMdrn_re_mean = mean_regridder.regrid(OM_drn, like)
OMdrn_re_sum  = sum_regridder.regrid(OM_drn, like)

OMriv_re = sum_regridder.regrid(OM_riv, like)
OMwel_re = sum_regridder.regrid(OM_wel, like)

inf_ponds_re = mean_regridder.regrid(inf_ponds["stage"], like)


#%% Analyze - errors
error_drn_2053_sum  = er(OMdrn_re_sum, meta_drn_2053)
bdgdrn_error = error_drn_2053_sum.mean().compute()

# polder area and infiltration ponds
error_riv_2053 = er(OMriv_re, meta_ghb_2053*(OMriv_re.notnull()==1))
bdgriv_error = error_riv_2053.mean().compute()
# error well
error_wel = er(OMwel_re,meta_wel_2053 )
bdgwel_error = error_riv_2053.mean().compute()

#%% Plotting
(fig, axs) = plt.subplots(3,1, figsize=(10,15))
error_drn_2053_sum.mean("layer").plot.imshow(ax=axs[0]) 
axs[0].set_title("Error drn")
error_riv_2053.mean("layer").plot.imshow(ax=axs[1])
axs[1].set_title("Error riv")
error_wel.mean("layer").plot.imshow(ax=axs[2])
axs[2].set_title("Error wel")
path_3 = pathlib.Path(f"reports/images/budget_errors.png")
plt.savefig(path_3, dpi=300)

#%% Plotting - cross sections
levels_conc  = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]
levels_depth = -1 * np.arange(0,130)
levels_conc_err = np.arange(0,20)/2-5
# Cross sections
starts = [
    (75000.0, 459948.0), # (x,y)
    (77423.0, 462817.0),
    (79234.0, 464828.4),
    (81880.4, 467911.6),
    (83718.9, 469707.8),
]
ends = [
    (87591.0, 449868.0), # (x,y)
    (92828.2, 450002.0),
    (93914.6, 452120.1),
    (95223.9, 455793.2),
    (96393.9, 460431.4),
]

for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(error_riv_2053, start=start, end=end)
    ax = CS.plot(yincrease = False)
    plt.title(f"Conc: CS {i+1}, meta perpendicular to coastline at t = 40y [d]")

# %%
