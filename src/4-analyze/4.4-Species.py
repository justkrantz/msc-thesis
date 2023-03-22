"""
- In this script the cross secitonal plots of (Stuyfzand, 1993) will be plotted.
- This is only for the metamodel, as the OM doesn't have species dimension
- This version shows groundwater salinity, its goal is to highlight the domains:
    - Saline groundwater
    - Fresh groundwater
    - Brackish groundwater
    - infiltration ponds species (AM)

- Transparency plots:
    https://matplotlib.org/stable/gallery/images_contours_and_fields/image_transparency_blend.html
"""

#%%
import imod
import numpy as np
import xarray as xr
import os
import geopandas
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pathlib
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
# To show both polder and AM, use combine_first, first the zero values need to be removed
polder_notnull = polder.where(polder>0.0)
AM_notnull = AM.where(AM>0.01)
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
# %% Transparency using AM, fresh and saline. CS par = parallel to coastline
# fresh saline levels
fresh_upper = 0.150   # g/l
brack_upper = 8.0000  # g/l 
# colorcode
SALT = tuple(np.array((249, 100, 29)) / 255)
# Fresh
CS_par_f = imod.select.cross_section_line(c1_meta.where(c1_meta<fresh_upper), start=start_loosduinen, end=end_katwijk).notnull()
CS_par_f = CS_par_f.where(CS_par_f!=0) # setting NaN to avoid overwriting plots
# Brackish
CS_par_b = imod.select.cross_section_line(c1_meta.where(c1_meta>fresh_upper).where(c1_meta<brack_upper), start=start_loosduinen, end=end_katwijk).notnull()
CS_par_b = CS_par_b.where(CS_par_b!=0) # setting NaN to avoid overwriting plots
# Saline
CS_par_s = imod.select.cross_section_line(c1_meta.where(c1_meta>brack_upper).where(CS_par_f.isnull()), start=start_loosduinen, end=end_katwijk).notnull()
CS_par_s = CS_par_s.where(CS_par_s!=0) # setting NaN to avoid overwriting plots
# AM
CS_AM = imod.select.cross_section_line(AM_notnull.where(AM_notnull!=0),  start=start_loosduinen, end=end_katwijk)
# values should be 
colors = ["Green", "darkorange", "Blue", "Gold" ]    # needed to make a colormap
levels = [1,    2,            3,      4,       5]    # needed to make a colormap

fig, ax = plt.subplots(figsize=(10,8))
# saline
CS_par_s_2 = 2*CS_par_s.where(CS_par_s["z"]<1.0).where(CS_par_s["s"]>1680) #to avoid NaN as "Saline"                  # 2 or 0
plot_3 = CS_par_s_2.plot(ax=ax, y="z", colors=colors, levels=levels, add_colorbar=False)
# fresh
CS_par_f_3 = 3*CS_par_f
plot_1 = CS_par_f_3.plot(ax=ax, y="z", colors=colors, levels=levels, add_colorbar=False)                              # 3 or 0
# Brackish
CS_par_b_4 = 4*CS_par_b
plot_2 = CS_par_b_4.plot(ax=ax, y="z", colors=colors, levels=levels, add_colorbar=False)                              # 4 or 0
# AM
CS_AM_mod = CS_AM.where(CS_AM>0.01).where(CS_AM!=0).notnull()                                                         # 1 or 0
plot_4 = CS_AM_mod.where(CS_AM_mod!=0).plot(ax=ax, y="z", colors=colors, levels=levels, add_colorbar=False)

# since quadmesh is not supported, proxy is required (https://matplotlib.org/2.0.2/users/legend_guide.html#proxy-legend-handles)
grn_patch     = mpatches.Patch(color='green' ,     label='Artificial Infiltration')
drkorn_patch  = mpatches.Patch(color='darkorange', label='Saline groundwater')
orn_patch     = mpatches.Patch(color='Gold'  ,     label='Brackish groundwater')
blu_patch     = mpatches.Patch(color='blue'  ,     label='Fresh groundwater')

ax.legend(handles=[grn_patch, orn_patch, drkorn_patch, blu_patch], loc="lower right")
plt.xlim(2500, 19000)
plt.ylim(-150,11)
plt.text(2800,12,"Loosduinen")
plt.text(18000,12, "Katwijk")
plt.title("Species after 100y simulation, cross section along coastline")
path2 = pathlib.Path(f"reports/images/1-scenario_FixedHead_onder/CS_long_species.png")
plt.savefig(path2, dpi=200)

# %%
