"""
In this script, the Flux Lower Boundary (FLF) of the OM and MM inside the study area will be investigated.
- FLF could be investigated per depth! 
- Histograms may not be needed.
"""
#%%
import numpy as np
import os
import imod
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas as pd
import pathlib
import geopandas
import matplotlib.patches as mpatches
#%%
os.chdir("c:/projects/msc-thesis")
#%% Import Data
flf_MM_SS = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\2-scenario_dichte_rand\bdgflf\bdgflf_201412312359_l*.idf")
flf_OM_SS = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\SS_run2_25m\dunea_transient_budget\bdgflf.zarr")
# Study area
gdf    = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
like   = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
raster = imod.prepare.rasterize(gdf, like)
#%% Process Data
flf_MM_SS_notime = flf_MM_SS.drop("time")
flf_OM_SS_2 = flf_OM_SS.drop("time").astype(np.float64).to_array()
# Import regridder & regrid original data
sum_regridder  = imod.prepare.Regridder(method="sum")
flf_OM_re      = sum_regridder.regrid(flf_OM_SS_2, like=like)
# Study area:
flf_MM_SA = flf_MM_SS_notime.where(raster==1)
flf_OM_SA = flf_OM_re.where(raster==1)
#%% Errors
def er(expected, actual):
    re = actual - expected
    return re
error_SS_global     = er(flf_OM_re, flf_MM_SS_notime)
error_SS_study_area = error_SS_global.where(raster==1)
#%% 
"""Histograms"""
# Statistics: global
mean        = error_SS_global.mean().compute().values
stdev       = error_SS_global.std().values
# Histogram
fig,ax = plt.subplots()
error_SS_global.plot.hist(ax=ax, xlim = [-100,100], bins=2000)
ax.set_title("SS flf error global")
plt.ylabel("frequency [N]")
plt.xlabel("$m^{3}$/d")
formatter = ticker.ScalarFormatter(useMathText=True)    # For scientific notation
formatter.set_scientific(True) 
formatter.set_powerlimits((-1,1)) 
ax.yaxis.set_major_formatter(formatter)
# text box hacky
def as_si(x, ndp):
    s = '{x:0.{ndp:d}e}'.format(x=x, ndp=ndp)
    m, e = s.split('e')
    return r'{m:s}\times 10^{{{e:d}}}'.format(m=m, e=int(e))
plt.text(30, 2.5e05,    r"$\mu = {0:s},$".format(as_si(mean , 2)))
plt.text(30, 2.3e05, r"$\sigma = {0:s} $".format(as_si(stdev, 2)))
path = pathlib.Path(f"reports/images/2-scenario_dichte_rand/SS_flf_global.png")
plt.savefig(path, dpi=300)
#%% Statistics: study area
mean        = error_SS_study_area.mean().compute().values
stdev       = error_SS_study_area.std().values
# Histogram
fig,ax = plt.subplots()
error_SS_study_area.plot.hist(ax=ax, xlim = [-100,100], bins=2000)
ax.set_title("SS flf error study area")
plt.ylabel("frequency [N]")
plt.xlabel("$m^{3}$/d")
formatter = ticker.ScalarFormatter(useMathText=True)    # For scientific notation
formatter.set_scientific(True) 
formatter.set_powerlimits((-1,1)) 
ax.yaxis.set_major_formatter(formatter)
# text box hacky
def as_si(x, ndp):
    s = '{x:0.{ndp:d}e}'.format(x=x, ndp=ndp)
    m, e = s.split('e')
    return r'{m:s}\times 10^{{{e:d}}}'.format(m=m, e=int(e))
plt.text(30, 1.1e04,    r"$\mu = {0:s},$".format(as_si(mean , 2)))
plt.text(30, 1.0e04, r"$\sigma = {0:s} $".format(as_si(stdev, 2)))
path = pathlib.Path(f"reports/images/2-scenario_dichte_rand/SS_flf_SA.png")
plt.savefig(path, dpi=300)

#%% Commands for looking at specific depths, global FLF of OM, MM

# OM

flf_OM_re.mean("variable").mean("time").isel(layer=9 ).plot.imshow(vmin=-100, vmax=100, cmap="RdBu_r")     # z = -    9.0 m
# %%
flf_OM_re.mean("variable").mean("time").isel(layer=21).plot.imshow(vmin=-100, vmax=100, cmap="RdBu_r")     # z = -   50.0 m
# %%
flf_OM_re.mean("variable").mean("time").isel(layer=26).plot.imshow(vmin=-100, vmax=100, cmap="RdBu_r")     # z = -   77.5 m
# %%
flf_OM_re.mean("variable").mean("time").isel(layer=31).plot.imshow(vmin=-100, vmax=100, cmap="RdBu_r")     # z = -  102.5 m
#%%

# MM

flf_MM_SS_notime.mean("time").isel(layer=9 ).plot.imshow(vmin=-100, vmax=100, cmap="RdBu_r")     # z = -    9.0 m
# %%
flf_MM_SS_notime.mean("time").isel(layer=21).plot.imshow(vmin=-100, vmax=100, cmap="RdBu_r")     # z = -   50.0 m
# %%
flf_MM_SS_notime.mean("time").isel(layer=26).plot.imshow()     # z = -   77.5 m
# %%
flf_MM_SS_notime.mean("time").isel(layer=31).plot.imshow()     # z = -  102.5 m
#%% Commands for looking at specific depths, SA Error
flf_err_layer10  = error_SS_study_area.mean("time").mean("variable").isel(layer=9 ).plot.imshow()   # z = -  9.0 m
flf_err_layer22  = error_SS_study_area.mean("time").mean("variable").isel(layer=21).plot.imshow()   # z = - 50.0 m
flf_err_layer27  = error_SS_study_area.mean("time").mean("variable").isel(layer=26).plot.imshow()   # z = - 77.5 m
flf_err_layer32  = error_SS_study_area.mean("time").mean("variable").isel(layer=31).plot.imshow()   # z = -102.5 m