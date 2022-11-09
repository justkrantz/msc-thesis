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
# Import output data
heads_2024   = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\head\head_202412282359_l*.idf")
conc_2024    = imod.idf.open(r"c:\projects\msc-thesis\data\4-output\conc\conc_202412282359_l*.IDF")

# %%
# Cross section plot 1 - along coastline
start_x1   = 75290.57
start_y1   = 456114.36
start_1    = (start_x1, start_y1)

end_x1 = 88652.26
end_y1 = 468778.83
end_1  = (end_x1, end_y1)

# Cross section plot 2 2 - perpendicular to coastline
start_x2   = 77344.272
start_y2   = 462731.01 
start_2    = (start_x2, start_y2)

end_x2 = 91785.39
end_y2 = 452746.85
end_2  = (end_x2, end_y2)

# The levels for heads [m NAP]
levels_head = [-6.0, -5.5, -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0] 
levels_conc = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 14.485, 15.0]

fig,ax = plt.subplots()
CS_25_1 = imod.select.cross_section_line(starting_head_regridded, start= start_1, end=end_1)
CS_25_1 = CS_25_1.plot(levels=levels_head, yincrease = False)
plt.title("Heads: CS along coastline at t = 0 [d]")


fig, ax = plt.subplots()
CS_500_1 = imod.select.cross_section_line(heads_2024, start=start_1, end=end_1)
CS_500_1 = CS_500_1.plot(levels=levels_head, yincrease = False)
plt.title("Heads: CS along coastline at t = 3650 [d]")

fig,ax = plt.subplots()
CS_25_2 = imod.select.cross_section_line(starting_conc_regridded, start= start_2, end=end_2)
CS_25_2 = CS_25_2.plot(levels=levels_conc, yincrease = False)
plt.title("Conc: CS perpendicular to coastline at t = 0 [d]")

fig, ax = plt.subplots()
CS_500_2 = imod.select.cross_section_line(conc_2024, start=start_2, end=end_2)
CS_500_2 = CS_500_2.plot(levels=levels_conc, yincrease = False)
plt.title("Conc: CS perpendicular to coastline at t = 3650 [d]")


# %%
