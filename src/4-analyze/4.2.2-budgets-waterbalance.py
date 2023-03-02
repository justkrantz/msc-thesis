"""" Water balance:
    IN:  
    - rch    (MM, OM)
    - ghb    (MM,   )   (inf ponds)
    - riv    (  , OM)   (inf ponds, polders)

    OUT: 
    - drn    (MM, OM)   (surface runoff, phreatic extraction)
    - well   (MM, OM)   (drainage for drinking water)
output:
- OM plot defined per calibration step (cond), 1.4.2

NOTE The SS budgets from MM calibration are defined in highlighted lines 82 and 84. 
     Change them according to output date of run
"""
#%%
import numpy as np
import os
import imod
import xarray as xr
import matplotlib.pyplot as plt
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
like_fine    = xr.open_dataarray(r"data/1-external/template_2d.nc")
gdf          = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
inf_ponds    = xr.open_dataset(r"c:\projects\msc-thesis\data\1-external\infiltration_ponds.nc")
inf_ponds = inf_ponds.isel(time=0, drop=True)
# Output: budgets from metamodel 
meta_drn_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgdrn\bdgdrn_205312312359_l*.idf").isel(time=0, drop=True)
meta_drn_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgdrn\bdgdrn_202412312359_l*.idf").isel(time=0, drop=True)
meta_drn_SS       = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgdrn\bdgdrn_201412312359_l*.idf").isel(time=0, drop=True)

meta_ghb_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgghb\bdgghb_205312312359_l*.idf").isel(time=0, drop=True)
meta_ghb_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgghb\bdgghb_202412312359_l*.idf").isel(time=0, drop=True)
meta_ghb_SS       = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgghb\bdgghb_201412312359_l*.idf").isel(time=0, drop=True)

meta_rch_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgrch\bdgrch_205312312359_l*.idf").isel(time=0, drop=True)
meta_rch_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgrch\bdgrch_202412312359_l*.idf").isel(time=0, drop=True)
# meta_drn_SS Unneccesary since rch will be the same

meta_wel_2053     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgwel\bdgwel_205312312359_l*.idf").isel(time=0, drop=True)
meta_wel_2024     = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\bdgwel\bdgwel_202412312359_l*.idf").isel(time=0, drop=True)
# meta_wel_SS Unneccessary since wel will be the same

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
like_fine["dx"] = xr.DataArray(25.0)
like_fine["dy"] = xr.DataArray(-25.0)
OMdrn_re_mean = mean_regridder.regrid(OM_drn, like)
OMdrn_re_sum  = sum_regridder.regrid(OM_drn, like)

OMriv_re = sum_regridder.regrid(OM_riv, like)
OMwel_re = sum_regridder.regrid(OM_wel, like)

inf_ponds_re  = mean_regridder.regrid(inf_ponds["stage"], like)
raster_MM     = imod.prepare.rasterize(gdf, like)           # study area, MM
raster_OM     = imod.prepare.rasterize(gdf, like_fine)      # study area, OM 

# Study area water balance, use sum:
# IN
rch_MM_SA = meta_rch_2053.where(raster_MM==1).sum("layer") # Assumed to be the same for both? check!
ghb_MM_SA = meta_ghb_SS.where(raster_MM==1).sum("layer") # Infiltration ponds, MM only
riv_OM_SA = OMriv_re.where(raster_MM==1).sum("layer")      # Infiltration ponds, OM only

# OUT
drn_MM_SA = meta_drn_SS.where(raster_MM==1).sum("layer") # Surface runoff and phreatic 
drn_OM_SA = OMdrn_re_sum.where(raster_MM==1).sum("layer")  # Surface runoff and phreatic

wel_MM_SA = meta_wel_2053.where(raster_MM==1).sum("layer") 
wel_OM_SA = OMwel_re.where(raster_MM==1).sum("layer")        
#%% Bar charts OM
fig,axs = plt.subplots()
WB_OM = ["riv", "drn", "well"]
axs = plt.bar(WB_OM, [riv_OM_SA.sum().compute(),   # Infiltration ponds
                      drn_OM_SA.sum().compute(),   # surface runoff (+pipe drainage?)
                      wel_OM_SA.sum().compute()])  # Wells
plt.title("SS Water Balance for OM")
plt.ylabel("$m^{3}$/d")
plt.grid()
path_3 = pathlib.Path(f"reports/images/Waterbalance_OM_sum.png")
plt.savefig(path_3, dpi=300)
#%% Bar Charts MM
fig,axs = plt.subplots()
WB_OM = ["ghb", "rch", "drn", "well"]
axs = plt.bar(WB_OM, [ghb_MM_SA.sum().compute(),   # infiltration ponds
                      rch_MM_SA.sum().compute(),   # precipitation
                      drn_MM_SA.sum().compute(),   # surface runoff (+ pipe drainage?)
                      wel_MM_SA.sum().compute()])  # Wells
plt.title("SS Water Balance for MM - cond6")
plt.ylabel("$m^{3}$/d")
plt.grid()
path_3 = pathlib.Path(f"reports/images/Waterbalance_MM_cond6_sum.png") # According to calibration 1.4.2
plt.savefig(path_3, dpi=300)
# %%
