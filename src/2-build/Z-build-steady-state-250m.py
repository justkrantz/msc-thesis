# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 14:14:45 2022

@author: krantz
    
    
- - - - - - - - - - !NOTES! - - - - - - - - - - 
    - This script investigates the use of sea as a ghb, 
    - 250x250m resolution
    - Changed moethod for regridding kh, kv to Sum regridder with relative weights
    
- - - - - - - -  - - - - - - - - - - - - - - - - - 
"""
# %%
import numpy as np
import imod
import xarray as xr
import matplotlib.pyplot as plt
import scipy.ndimage.morphology
import pandas as pd
import dask.array
import os
import datetime
import pathlib

from dask.diagnostics import ProgressBar

os.chdir(r"C:\projects\Example_huite\2-interim\2-interim")

# %%

# 1.1 Inputs
# To be modified:
# Will be modified after regridding
CL_25 = xr.open_dataarray("chloride.nc")
wells = pd.read_csv("wells.csv")  # With time!
RCH = xr.open_dataset("recharge.nc")  # With time!

# 1.2 Time

# The entries are dropped, except the first, which is the average
wells_2014 = wells[wells["time"] == "2014-12-31 23:59:59"]


# Other
conductivity = xr.open_dataset("conductivity.nc")
template = xr.open_dataarray("template.nc")
template_2d = xr.open_dataarray("template_2d.nc")
starting_head = xr.open_dataarray("starting-head.nc")
kh = conductivity["kh"]
kv = conductivity["kv"]
GHB = xr.open_dataset("generalheadboundary.nc")
ghb_head = GHB["stage"]
ghb_cond = GHB["cond"]
ghb_conc = GHB["conc"]
ghb_dens = GHB["density"]

# River package - combine infiltration_ponds and river - drop the time
inf_ponds = xr.open_dataset("infiltration_ponds.nc", chunks={"time": 10}).drop(
    "is_pond_2D"
)
inf_ponds_mean = inf_ponds.mean("time", skipna=True)
river_1 = xr.open_dataset("river.nc", chunks={"time": 10})
riv_mean = river_1.mean("time", skipna=True)

# combine the two:
river = riv_mean.combine_first(inf_ponds_mean)
riv_stage = river["stage"]
riv_cond = river["cond"]
riv_bot = river["bot"]
riv_dens = river["density"]

# Sea - as a constant head to be added to the ghb
sea = xr.open_dataset("sea.nc")
sea_stage = sea["stage"]
sea_cond = sea["cond"]
sea_conc = sea["conc"]
sea_density = sea["density"]

ghb_comb = GHB.combine_first(sea)
ghb_comb_head = ghb_comb["stage"]
ghb_comb_cond = ghb_comb["cond"]
ghb_comb_conc = ghb_comb["conc"]
ghb_comb_dens = ghb_comb["density"]

# For SS - add river also to the ghb package - not working
ghb_all = ghb_comb.combine_first(river)
ghb_all_head = ghb_all["stage"]
ghb_all_cond = ghb_all["cond"]
ghb_all_conc = ghb_all["conc"]
ghb_all_dens = ghb_all["density"]


# %%
""""
Regridding - ibound
"""


def round_extent(extent, cellsize):
    """Increases the extent until all sides lie on a coordinate
    divisible by cellsize."""
    xmin, ymin, xmax, ymax = extent
    xmin = np.floor(xmin / cellsize) * cellsize
    ymin = np.floor(ymin / cellsize) * cellsize
    xmax = np.ceil(xmax / cellsize) * cellsize
    ymax = np.ceil(ymax / cellsize) * cellsize
    return xmin, ymin, xmax, ymax


x_old = template.coords["x"]
y_old = template.coords["y"]

dx_1 = 250
xmin_1 = x_old[0]
xmax_1 = x_old[-1]


dy_1 = -250
ymin_1 = y_old[-1]
ymax_1 = y_old[0]

xmin_1, ymin_1, xmax_1, ymax_1 = round_extent((xmin_1, ymin_1, xmax_1, ymax_1), dx_1)

layer = np.array(
    [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
    ],
)

Empty_2d_DataArray = imod.util.empty_2d(
    dx_1,
    xmin_1,
    xmax_1,
    dy_1,
    ymin_1,
    ymax_1,
)
like_1 = Empty_2d_DataArray
like_1_ds = like_1.to_dataset(name=("like_1_ds"))

harmonic_regridder = imod.prepare.Regridder(method="harmonic_mean")
sum_regridder = imod.prepare.Regridder(method="sum", use_relative_weights=True)
mean_regridder = imod.prepare.Regridder(method="mean")
cond_regridder = imod.prepare.Regridder(method="conductance")

template_re = sum_regridder.regrid(template, like_1)

# Creates a 2d layer of the study domain (clipped)
domain2d = starting_head.isel(z=-1, drop=True).notnull()

# two conditions
ibound = kh.notnull() & domain2d

# Now apply regridding

ibound_re = sum_regridder.regrid(ibound, like_1)

# 25 bij 25 --> 250 x 250: maximaal 10 * 10 = 100 cellen; 50 is de helft
new_ibound = ibound_re > 50
new_ibound = new_ibound.assign_coords(
    layer=("z", np.arange(1, 50))
)  # Add lost coordinates again,

# Loss of ztop in regridding, therefore take from original
top = ibound.coords["ztop"]
# Loss of zbot in regridding, therefore take from original
bottom = ibound.coords["zbot"]

# needed for indexing later:

# For the surface level, a drain
top_top = top.where(new_ibound != 0).max("z")
layer_top = new_ibound.layer.where(new_ibound != 0).min(
    "z"
)  # For the surface level, which layers

# For the drainage package
top3d = top.where(new_ibound != 0)
surface_level = top3d.max("z")
is_top = top3d == surface_level
drain_elevation = top3d.where(is_top)


# %%
""" 
Regridding - other input data
"""
# applying same method to starting head
SH_re = mean_regridder.regrid(starting_head, like_1)
new_SH = SH_re.where(new_ibound)

RCH_re = mean_regridder.regrid(RCH["recharge"], like_1)
rch_mean = RCH_re.mean("layer").mean("time")
# To investigate the effect
rch_double = rch_mean * 2

# River
riv_stage_re = mean_regridder.regrid(riv_stage, like_1)
riv_cond_re = mean_regridder.regrid(riv_cond, like_1)
riv_bot_re = mean_regridder.regrid(riv_bot, like_1)
riv_dens_re = mean_regridder.regrid(riv_dens, like_1)


# Conductivities
kh_re = mean_regridder.regrid(kh, like_1)
kv_re = harmonic_regridder.regrid(kv, like_1)

new_kh = kh_re.where(new_ibound)
new_kh = new_kh.assign_coords(layer=("z", np.arange(1, 50)))
new_kh = new_kh.assign_coords(dz=kh["dz"]).drop(["dx", "dy"])

new_kv = kv_re.where(new_ibound)
new_kv = new_kv.assign_coords(layer=("z", np.arange(1, 50)))
new_kv = new_kv.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])

# Starting concentrations
CL_re = mean_regridder.regrid(CL_25, like_1)
new_CL = CL_re.where(new_ibound)
new_CL = new_CL.assign_coords(layer=("z", np.arange(1, 50)))


ghb_head_re = mean_regridder.regrid(ghb_all_head, like_1)
ghb_cond_re = cond_regridder.regrid(ghb_all_cond, like_1)
ghb_conc_re = mean_regridder.regrid(ghb_all_conc, like_1)
ghb_dens_re = mean_regridder.regrid(ghb_all_dens, like_1)


# %%
# Add midding layer coordinates
new_ghb_head = ghb_head_re.assign_coords(layer=("z", np.arange(1, 50)))
new_ghb_cond = ghb_cond_re.assign_coords(layer=("z", np.arange(1, 50)))
new_ghb_conc = ghb_conc_re.assign_coords(layer=("z", np.arange(1, 50)))
new_ghb_dens = ghb_dens_re.assign_coords(layer=("z", np.arange(1, 50)))

new_riv_stage_re = riv_stage_re.assign_coords(layer=("z", np.arange(1, 50)))
new_riv_cond_re = riv_cond_re.assign_coords(layer=("z", np.arange(1, 50)))
new_riv_bot_re = riv_bot_re.assign_coords(layer=("z", np.arange(1, 50)))
new_riv_dens_re = riv_dens_re.assign_coords(layer=("z", np.arange(1, 50)))

# Add missing dz coordinates
new_ghb_head = new_ghb_head.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])
new_ghb_cond = new_ghb_cond.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])
new_ghb_conc = new_ghb_conc.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])
new_ghb_dens = new_ghb_dens.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])

riv_stage_final = new_riv_stage_re.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])
riv_cond_final = new_riv_cond_re.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])
riv_bot_final = new_riv_bot_re.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])
riv_dens_final = new_riv_dens_re.assign_coords(dz=kv["dz"]).drop(["dx", "dy"])


# %%
# Fully fresh starting concentrations
CL_fresh = new_CL.notnull() * new_CL.min()

# %%

"""
Build the iMOD-WQ model for fully fresh groundwater starting conditions
"""
m_f = imod.wq.SeawatModel("50y_fresh")

m_f["bas"] = imod.wq.BasicFlow(
    ibound=new_ibound,
    top=top[0],
    bottom=bottom.zbot,
    starting_head=new_SH,
    inactive_head=-9999.0,
)  # """ Value error: may not have correct ibound """
m_f["lpf"] = imod.wq.LayerPropertyFlow(k_horizontal=new_kh, k_vertical=new_kv)
# default effective porosity = 0.35
m_f["btn"] = imod.wq.BasicTransport(icbund=new_ibound, starting_concentration=CL_fresh)

# Total Variation Diminishing (TVD) Advection
# Courant number is the number of cells, or fraction of a cell, for which advection will be allowed in one transport step
m_f["adv"] = imod.wq.AdvectionTVD(courant=1.0)
m_f["dsp"] = imod.wq.Dispersion(longitudinal=0.001)
m_f["vdf"] = imod.wq.VariableDensityFlow(density_concentration_slope=0.71)
m_f["pcg"] = imod.wq.PreconditionedConjugateGradientSolver(
    max_iter=150,  # max number of outer iterations
    inner_iter=30,  # number of inner iterations
    hclose=0.001,  # head change criterion for convergence
    rclose=0.1,  # residual convergence criterion
    relax=0.98,  # relaxation parameter
    damp=1.0,  # damping factor, equal to 1 means no damping
)
m_f["gcg"] = imod.wq.GeneralizedConjugateGradientSolver(
    max_iter=150,  #
    inner_iter=30,  #
    cclose=1.0e-6,  # convergence criterion in terms of relative concentration
    preconditioner="mic",  #
    lump_dispersion=True,  #
)

m_f["ghb"] = imod.wq.GeneralHeadBoundary(
    new_ghb_head, new_ghb_cond, new_ghb_dens, concentration=None, save_budget=True
)
m_f["rch"] = imod.wq.RechargeHighestActive(
    rate=rch_mean, concentration=0.0, save_budget=True
)
m_f["oc"] = imod.wq.OutputControl(
    save_head_idf=True, save_concentration_idf=True, save_budget_idf=True
)

# Remaining packages

m_f["wel"] = imod.wq.Well(
    id_name=wells_2014["idcode"],
    x=wells_2014["x"],
    y=wells_2014["y"],
    rate=wells_2014["rate"].min(),
    layer=wells_2014["layer"],
    save_budget=True,
)

# m_f["riv"] = imod.wq.River(
#    riv_stage_final,
#    riv_cond_final,
#    riv_bot_final,
#    riv_dens_final,
#    save_budget=True
# )


is_cond = is_top * new_ghb_cond.max()
is_cond_2 = is_cond.where(is_top)

is_cond_lower = is_top * 250
is_cond_2_lower = is_cond_lower.where(is_top)

m_f["drn"] = imod.wq.Drainage(
    drain_elevation,  # Take the top of ibound
    # maximum conductance found in the model is 6250
    is_cond_2_lower,
    save_budget=True,
)


# Time discretization
m_f.create_time_discretization(
    additional_times=["2014-12-31T23:59:59.000000000", "2015-01-01T00:00:00.000000000"]
)
m_f["time_discretization"].dataset["transient"] = False

modeldir_f = pathlib.Path("50y_f")
m_f.write(modeldir_f, result_dir="C:/projects/Example_huite/2-interim/2-interim/50y_f")
