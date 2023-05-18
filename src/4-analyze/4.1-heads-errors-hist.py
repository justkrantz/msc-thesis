#%%
"""
Analyze the SS heads of metamodel, compare with 25m heads:
- Histogram
- TOP VIEW OF ERROR HEADS
"""
#%%
import numpy as np
import os
import imod
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import geopandas
import pathlib
from matplotlib import ticker
#%%
os.chdir("c:/projects/msc-thesis")
#%% Import data
like = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
gdf  = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp")
heads_SS_OM_zarr = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\head_ss_t0.zarr")
heads_SS_MM      = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\3-scenario_FixedHead_rand\head\head_201412312359_l*.idf")
starting_head_MM = imod.idf.open(r"c:\projects\msc-thesis\data\3-input\SS_1\bas\starting_head_l*.idf")
#%% Process data
heads_SS_OM = heads_SS_OM_zarr["head"].drop("time").astype(np.float64)
heads_SS_MM_notime = heads_SS_MM.isel(time=0, drop=True)
raster             = imod.prepare.rasterize(gdf, like) # study area
# Import regridder & regrid OM data
mean_regridder = imod.prepare.Regridder(method="mean")
heads_SS_OM_re = mean_regridder.regrid(heads_SS_OM, like=like)
#%% Calculate errors
def er(expected, actual):
    re = actual - expected
    return re
error_SS_global     = er(heads_SS_OM_re, heads_SS_MM_notime)
error_SS_study_area = error_SS_global.where(raster==1)
# %% Statistics: global
mean        = error_SS_global.mean().compute().values
stdev       = error_SS_global.std().values
# Histogram
fig,ax = plt.subplots()
error_SS_global.plot.hist(ax=ax, xlim = [-4,4], bins=200)
ax.set_title("SS heads error global")
plt.ylabel("frequency [N]")
plt.xlabel("error [m]")
formatter = ticker.ScalarFormatter(useMathText=True)    # For scientific notation
formatter.set_scientific(True) 
formatter.set_powerlimits((-1,1)) 
ax.yaxis.set_major_formatter(formatter)
# text box hacky
def as_si(x, ndp):
    s = '{x:0.{ndp:d}e}'.format(x=x, ndp=ndp)
    m, e = s.split('e')
    return r'{m:s}\times 10^{{{e:d}}}'.format(m=m, e=int(e))
plt.text(1, 35000,    r"$\mu = {0:s},$".format(as_si(mean , 2)))
plt.text(1, 31000, r"$\sigma = {0:s} $".format(as_si(stdev, 2)))
path = pathlib.Path(r"C:\projects\msc-thesis\reports\images\2-scenario_dichte_rand/SS_head_global.png")
plt.savefig(path, dpi=300)
#%% Statistics study area
mean  = error_SS_study_area.mean().compute().values
stdev = error_SS_study_area.std().values 
# Histogram study area
fig,ax = plt.subplots()
error_SS_study_area.plot.hist(ax=ax, xlim = [-4,4], bins=200)
ax.set_title("SS heads error study area")
plt.ylabel("frequency [N]")
plt.xlabel("error [m]")
formatter = ticker.ScalarFormatter(useMathText=True)    # For scientific notation
formatter.set_scientific(True) 
formatter.set_powerlimits((-1,1)) 
ax.yaxis.set_major_formatter(formatter) 
# text box hacky
def as_si(x, ndp):
    s = '{x:0.{ndp:d}e}'.format(x=x, ndp=ndp)
    m, e = s.split('e')
    return r'{m:s}\times 10^{{{e:d}}}'.format(m=m, e=int(e))
plt.text(1, 2000,    r"$\mu = {0:s},$".format(as_si(mean , 2)))
plt.text(1, 1800, r"$\sigma = {0:s} $".format(as_si(stdev, 2)))
path = pathlib.Path(r"C:\projects\msc-thesis\reports\images\2-scenario_dichte_rand/SS_head_SA.png")
plt.savefig(path, dpi=300)

# %% Top view plot error heads
Katwijk_xy       = (88055, 468500)
Scheveningen_xy  = (79240, 458415)
Voorschoten_xy   = (90521, 459909)  
# up to 32m depth
fig, (ax1, ax2) = plt.subplots(2,1, sharex=True, sharey=True, figsize = (10,12))
error_SS_global.mean("layer").plot.imshow(ax=ax1, vmin=-1.5, vmax=1.5, cmap ="RdBu")
ax1.set_title("mean hydraulic heads error over z ")
ax1.annotate('Katwijk', xy=Katwijk_xy, xytext=(80000, 467500),
            arrowprops=dict(arrowstyle="simple", facecolor='black'),
            )
ax1.annotate('Scheveningen', xy=Scheveningen_xy, xytext=(76000, 465000),
            arrowprops=dict(arrowstyle="simple", facecolor='black'),
            )
ax1.annotate('Voorschoten', xy=Voorschoten_xy, xytext=(91000, 450500),
            arrowprops=dict(arrowstyle="simple", facecolor='black'),
            )
error_SS_global.isel(layer=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]).mean("layer").plot.imshow(ax=ax2, vmin=-1.5, vmax=1.5, cmap="RdBu")
ax2.set_title("mean hydraulic heads error to z = -32.5m")
ax2.annotate('Katwijk', xy=Katwijk_xy, xytext=(80000, 467500),
            arrowprops=dict(arrowstyle="simple", facecolor='black'),
            )
ax2.annotate('Scheveningen', xy=Scheveningen_xy, xytext=(76000, 465000),
            arrowprops=dict(arrowstyle="simple", facecolor='black'),
            )
ax2.annotate('Voorschoten', xy=Voorschoten_xy, xytext=(91000, 450500),
            arrowprops=dict(arrowstyle="simple", facecolor='black'),
            )
path = pathlib.Path(r"C:\projects\msc-thesis\reports\images\2-scenario_dichte_rand/SS_errors_topview.png")
plt.savefig(path, dpi=300)
#%% Error over depth
fig,ax = plt.subplots(figsize= (5,6))
error_SS_study_area.mean("x").mean("y").plot(y="z", ax=ax)
plt.xlabel("mean absolute error over study area [m]")
plt.ylabel("depth [m]")
plt.xlim(-1.25, 1.25)
plt.title("")
plt.grid()

# %%
