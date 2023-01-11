#%%
"""
Analyze the results from the outpuy folder
- Import output data
- Create a series of cross sections perpendicular to the coastline
    - For heads, concentrations and time

"""
#%%
import numpy as np
import imod
import xarray as xr
import matplotlib.pyplot as plt
import scipy.ndimage.morphology
import pandas as pd
import pathlib
#%%
# Import input data
starting_head_regridded = imod.idf.open(r"c:\projects\msc-thesis\data\3-input\SS_1\bas\starting_head_l*.idf") # NOTE That these are not used as input. instead, the SS heads by 25m model are now used as input
starting_conc_regridded = imod.idf.open(r"c:\projects\msc-thesis\data\3-input\SS_1\btn\starting_concentration_l*.idf")
# Import data 25m model
conc_25m    = xr.open_zarr(r"data\1-external\data-25-run-1\conc-selection.zarr")
heads_ss_25 = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\head_ss_t0.zarr").drop("time")
starting_conc  = xr.open_zarr(r"c:\projects\msc-thesis\data\1-external\data-25-run-1\conc-selection.zarr").isel(time=0, drop=True)
# Output data: Heads
heads_2024   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_202412312359_l*.idf")

# Output data: concentrations
c1_2024 = imod.idf.open(r"data\4-output\conc\conc_c1_202412312359_l*.idf") # Cl
c2_2024 = imod.idf.open(r"data\4-output\conc\conc_c2_202412312359_l*.idf") # AM
c3_2024 = imod.idf.open(r"data\4-output\conc\conc_c3_202412312359_l*.idf") # Polders

c1_2054 = imod.idf.open(r"data\4-output\conc\conc_c1_205412312359_l*.IDF") # Cl
c2_2054 = imod.idf.open(r"data\4-output\conc\conc_c2_205412312359_l*.IDF") # AM
c3_2054 = imod.idf.open(r"data\4-output\conc\conc_c3_205412312359_l*.IDF") # Polders

# import regridder
mean_regridder = imod.prepare.Regridder(method="mean")

# Process for plotting:
Cl_2024 = c1_2024.where(c1_2024<17)
AM_2024 = c2_2024.where(c2_2024<2 )
PO_2024 = c3_2024.where(c3_2024<2 )

Cl_2054 = c1_2054.where(c1_2054<17)
AM_2054 = c2_2054.where(c2_2054<2 )
PO_2054 = c3_2054.where(c3_2054<2 )

#%%
# The levels 
levels_head = [-6.0, -5.5, -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0] 
levels_conc = [0.0,   2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]
levels_spec = 1/20*np.arange(1,20)

# Cross sections
# Series of start- and end coordinates for cross sections

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
#%%
# Heads (t = 10y)
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(heads_2024, start=start, end=end)
    ax = CS.plot(levels=levels_head, yincrease = False)
    plt.title(f"Head: CS {i+1} perpendicular to coastline at t = 3650 [d]")
    #path = pathlib.Path(f"reports/images/cross_sections/head_cross_section_10y_{i+1}.png")
    #path.parent.mkdir(exist_ok=True, parents=True)
    #fig.savefig(path, dpi=300)

# Heads (t = 0)
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(starting_head_regridded, start=start, end=end)
    ax = CS.plot(levels=levels_head, yincrease = False)
    plt.title(f"Head: CS {i+1} perpendicular to coastline at t = 0 [d]")
    #path = pathlib.Path(f"reports/images/cross_sections/head_cross_section_t0_{i+1}.png")
    #path.parent.mkdir(exist_ok=True, parents=True)
    #fig.savefig(path, dpi=300)
#%%
"""
Concentrations from 250m model
"""
# Cl at t = 10y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(Cl_2024, start=start, end=end)
    ax = CS.plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 3650 [d]")
#    path = pathlib.Path(f"reports/images/cross_sections/concentration_Cl_cross_section_10y_{i+1}.png")
#    path.parent.mkdir(exist_ok=True, parents=True)
#    fig.savefig(path, dpi=300)
#%%
# Cl at t=40y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(Cl_2054, start=start, end=end)
    ax = CS.plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 14610 [d]")
#    path = pathlib.Path(f"reports/images/cross_sections/concentration_Cl_cross_section_40y_{i+1}.png")
#    path.parent.mkdir(exist_ok=True, parents=True)
#    fig.savefig(path, dpi=300)

# To save the figures:
#    path = pathlib.Path(f"reports/images/cross_sections/conc_cross_section_20y_{i+1}.png")
#    path.parent.mkdir(exist_ok=True, parents=True)
#    fig.savefig(path, dpi=300)

#%%
"""
Concentrations from 25m model
"""
# initial concentration
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(conc_25m.isel(time=0), start=start, end=end)
    ax = CS["conc"].plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 0 [d]")    
# after 10y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(conc_25m.isel(time=1), start=start, end=end)
    ax = CS["conc"].plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 3650 [d]")
# after 20y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(conc_25m.isel(time=2), start=start, end=end)
    ax = CS["conc"].plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 7300 [d]")
# after 30y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(conc_25m.isel(time=3), start=start, end=end)
    ax = CS["conc"].plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 10950 [d]")
# after 40y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(conc_25m.isel(time=4), start=start, end=end)
    ax = CS["conc"].plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 14610 [d]")

#%% 
# [AM] = infiltration ponds
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(AM_2024, start=start, end=end)
    ax = CS.plot(yincrease = False)
    plt.title(f"[AM]: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# %%
# [polders]
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(PO_2024, start=start, end=end)
    ax = CS.plot(yincrease = False)
    plt.title(f"[polders]: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# %%
# Try to combine the two using 
# https://matplotlib.org/stable/gallery/images_contours_and_fields/image_transparency_blend.html 

levels_polder_AM = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS1 = imod.select.cross_section_line(AM_2024, start=start, end=end)
    ax = CS1.plot( yincrease = False)
    CS2 = imod.select.cross_section_line(PO_2024, start=start, end=end)
    ax = CS2.plot( yincrease = False)
    plt.title(f"[polders and AM]: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# %%
