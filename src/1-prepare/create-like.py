# %%

import imod
import numpy as np
import xarray as xr

# %%

def round_extent(extent, cellsize):
    """Increases the extent until all sides lie on a coordinate
    divisible by cellsize."""
    xmin, ymin, xmax, ymax = extent
    xmin = np.floor(xmin / cellsize) * cellsize
    ymin = np.floor(ymin / cellsize) * cellsize
    xmax = np.ceil(xmax / cellsize) * cellsize
    ymax = np.ceil(ymax / cellsize) * cellsize
    return xmin, ymin, xmax, ymax

# %%
template = xr.open_dataarray("data/1-external/template.nc")

x_old = template.coords["x"]
y_old = template.coords["y"]

dx_1 = 250
xmin_1 = x_old[0]
xmax_1 = x_old[-1]


dy_1 = -250
ymin_1 = y_old[-1]
ymax_1 = y_old[0]

xmin_1, ymin_1, xmax_1, ymax_1 = round_extent((xmin_1, ymin_1, xmax_1, ymax_1), dx_1)


like = imod.util.empty_2d(
    dx_1,
    xmin_1,
    xmax_1,
    dy_1,
    ymin_1,
    ymax_1,
)
like_ds = like.to_dataset(name=("like"))

like_ds.to_netcdf("data/2-interim/like.nc")

# %%