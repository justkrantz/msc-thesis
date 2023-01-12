"""
- In this script the cross secitonal plots of (Stuyfzand, 1993) will be plotted.
- This is only for the metamodel, as the OM doesn't have species dimension
- Transparency plots:
    https://matplotlib.org/stable/gallery/images_contours_and_fields/image_transparency_blend.html
"""

#%%
import imod
import numpy as np
import xarray as xr
import os
import geopandas
import matplotlib.pyplot as plt
# %%
os.chdir("c:/projects/msc-thesis")
# %% Data
like   = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/like.nc")
ibound = xr.open_dataarray(r"c:/projects/msc-thesis/data/2-interim/ibound_coarse.nc") 
gdf    = geopandas.read_file(r"c:\projects\msc-thesis\data\1-external\Polygon.shp") # study Area
surface_level = xr.open_dataarray("data/2-interim/surface_level_without_sea.nc")
# output data 
c1_meta = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c1*.IDF").isel(time=-1, drop=True)
c2_meta = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c2*.IDF").isel(time=-1, drop=True)
c3_meta = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c3*.IDF").isel(time=-1, drop=True)
# Process data
Cl     = c1_meta.where(c1_meta != 1e30).where(~(c1_meta < 0.0), other=0.0).isel(species=0, drop=True)
AM     = c2_meta.where(c2_meta != 1e30).where(~(c2_meta < 0.0), other=0.0).isel(species=0, drop=True)
polder = c3_meta.where(c3_meta != 1e30).where(~(c3_meta < 0.0), other=0.0).isel(species=0, drop=True)
# for regridding to study area:
mean_regridder = imod.prepare.Regridder(method="mean") 
# %% Plotting transparency plots (only AM and polders)

# To combine both datasets using combine_first, first the zero values need to be removed
polder_notnull = polder.where(polder>0.0)
AM_notnull = AM.where(AM>0.0)
# Then make one of the dataarrays negative, to plot both without losing species info
polder_negative = -1*polder_notnull
combined_da = AM_notnull.combine_first(polder_negative)

# cross section parallel to coastline
start_loosduinen = (75471,453198)
end_katwijk      = (87789.1,468649.0)
CS_par = imod.select.cross_section_line(combined_da, start=start_loosduinen, end=end_katwijk)

# Plot both
fig, (ax1, ax2, ax3) = plt.subplots(3,1, figsize=(10,15))
combined_da.isel(y=35).plot(ax=ax1,y="z", cmap='RdYlBu')
ax1.set_title("Cross section perpendicular to coastline")
combined_da.isel(layer=10).plot.imshow(ax=ax2,cmap='RdYlBu')
ax2.set_title("top view, -11mNAP")
CS_par.plot(ax=ax3,y="z", cmap = "RdYlBu")
ax3.set_title("Cross section along coastline: [Loosduinen - Katwijk]")
# %%


fig, ax = plt.subplots()
c2_meta.where(c2_meta != 1.0e30).where(c2_meta > 0.1).isel(y=20).plot(ax=ax, y="z", colors=[SALT], levels=[0.1])
c3_meta.where(c3_meta != 1.0e30).where(c3_meta > 0.1).isel(y=20).plot(ax=ax, y="z")
# %%

LEVELS = [0.150, 1.0]  # 150 mg/L, 1000 mg/L
SALT = tuple(np.array((249, 100, 29)) / 255)
# %%

#c2_meta.where(c2_meta != 1.0e30).where(c2_meta > 0.1).isel(y=20).plot(ax=ax, y="z", colors=[SALT], levels=[0.1])
