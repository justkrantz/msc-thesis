#%%
import numpy as np
import imod
import os
import xarray as xr
#%%
os.chdir("c:/projects/msc-thesis")

#%%

oc= imod.wq.OutputControl(
    save_head_idf=True, save_concentration_idf=True, save_budget_idf=True
)

pcg = imod.wq.PreconditionedConjugateGradientSolver(
    max_iter=150,  # max number of outer iterations
    inner_iter=30,  # number of inner iterations
    hclose=0.001,  # head change criterion for convergence
    rclose=0.1,  # residual convergence criterion
    relax=0.98,  # relaxation parameter
    damp=1.0,  # damping factor, equal to 1 means no damping
)
gcg = imod.wq.GeneralizedConjugateGradientSolver(
    max_iter=150,  #
    inner_iter=30,  #
    cclose=1.0e-6,  # convergence criterion in terms of relative concentration
    preconditioner="mic",  #
    lump_dispersion=True,  #
)

# Save
oc.dataset.to_netcdf("data/3-input/oc.nc")
pcg.dataset.to_netcdf("data/3-input/pcg.nc")
gcg.dataset.to_netcdf("data/3-input/gcg.nc")

# %%
