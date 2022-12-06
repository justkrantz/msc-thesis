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
starting_head_regridded = imod.idf.open(r"c:\projects\msc-thesis\data\3-input\SS_1\bas\starting_head_l*.idf")
starting_conc_regridded = imod.idf.open(r"c:\projects\msc-thesis\data\3-input\SS_1\btn\starting_concentration_l*.idf")
# Import output data 25m model
conc_25m = xr.open_zarr(r"data\1-external\data-25-run-1\conc-selection.zarr")

# Import output data
heads_2024   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_202412312359_l*.idf")

conc_polder_2024    = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c3_202412312359_l*.idf")
conc_AM_2024    = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c2_202412312359_l*.idf")
conc_Cl_2024    = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c1_202412312359_l*.idf")
conc_Cl_2054    = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_c1_205412312359_l*.idf")

c_polder_2024 = conc_polder_2024.where(conc_polder_2024<2)
c_AM_2024     = conc_AM_2024.where(conc_AM_2024<2)
c_Cl_2024     = conc_Cl_2024.where(conc_Cl_2024<17)

c_Cl_2054   = conc_Cl_2054.where(conc_Cl_2054<17)

#%%
# The levels for heads [m NAP]
levels_head = [-6.0, -5.5, -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0] 
levels_conc = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0]

# %% Cross sections
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
# Heads (t = 20y)
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(heads_2024, start=start, end=end)
    ax = CS.plot(levels=levels_head, yincrease = False)
    plt.title(f"Head: CS {i+1} perpendicular to coastline at t = 3650 [d]")
    path = pathlib.Path(f"reports/images/cross_sections/head_cross_section_20y_{i+1}.png")
    path.parent.mkdir(exist_ok=True, parents=True)
    fig.savefig(path, dpi=300)

# Heads (t = 0)
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(starting_head_regridded, start=start, end=end)
    ax = CS.plot(levels=levels_head, yincrease = False)
    plt.title(f"Head: CS {i+1} perpendicular to coastline at t = 0 [d]")
    path = pathlib.Path(f"reports/images/cross_sections/head_cross_section_t0_{i+1}.png")
    path.parent.mkdir(exist_ok=True, parents=True)
    fig.savefig(path, dpi=300)
#%%
"""
Concentrations from 250m model
"""
# Cl at t = 10y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(c_Cl_2024, start=start, end=end)
    ax = CS.plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# Cl at t=40y
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(c_Cl_2054, start=start, end=end)
    ax = CS.plot(levels=levels_conc, yincrease = False, cmap = "turbo")
    plt.title(f"Conc: CS {i+1} perpendicular to coastline at t = 14610 [d]")


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
    CS = imod.select.cross_section_line(c_AM, start=start, end=end)
    ax = CS.plot(yincrease = False)
    plt.title(f"[AM]: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# %%
# [polders]
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS = imod.select.cross_section_line(c_polder, start=start, end=end)
    ax = CS.plot(yincrease = False)
    plt.title(f"[polders]: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# %%
# Try to combine the two using 
# https://matplotlib.org/stable/gallery/images_contours_and_fields/image_transparency_blend.html 

levels_polder_AM = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
for i, (start, end) in enumerate(zip(starts, ends)):
    fig, ax = plt.subplots()
    CS1 = imod.select.cross_section_line(c_AM, start=start, end=end)
    ax = CS1.plot( yincrease = False)
    CS2 = imod.select.cross_section_line(c_polder, start=start, end=end)
    ax = CS2.plot( yincrease = False)
    plt.title(f"[polders and AM]: CS {i+1} perpendicular to coastline at t = 3650 [d]")

# %%
