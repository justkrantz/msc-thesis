#%%
import imod
import xarray as xr
import os
import pathlib
#%%
os.chdir("c:/projects/msc-thesis/")
#%%
# Read input for model

bas = imod.wq.BasicFlow.from_file("data/3-input/bas.nc")
lpf = imod.wq.LayerPropertyFlow.from_file("data/3-input/lpf.nc")
btn = imod.wq.BasicTransport.from_file("data/3-input/btn.nc")
dsp = imod.wq.Dispersion.from_file("data/3-input/dsp.nc")
adv = imod.wq.AdvectionTVD.from_file("data/3-input/adv.nc")
vdf = imod.wq.VariableDensityFlow.from_file("data/3-input/vdf.nc")
ghb = imod.wq.GeneralHeadBoundary.from_file("data/3-input/ghb.nc")
rch = imod.wq.RechargeHighestActive.from_file("data/3-input/rch.nc")
wel = imod.wq.Well.from_file("data/3-input/wel.nc")
drn = imod.wq.Drainage.from_file("data/3-input/drn.nc")
# %%

oc  = imod.wq.OutputControl.from_file("data/3-input/oc.nc" )
pcg = imod.wq.PreconditionedConjugateGradientSolver.from_file("data/3-input/pcg.nc")
gcg = imod.wq.GeneralizedConjugateGradientSolver.from_file("data/3-input/gcg.nc")

#%%
# Initialize model

m_ss = imod.wq.SeawatModel("SS_1")

m_ss["bas"] = bas
m_ss["lpf"] = lpf
m_ss["btn"] = btn
m_ss["dsp"] = dsp
m_ss["adv"] = adv
m_ss["vdf"] = vdf
m_ss["ghb"] = ghb
m_ss["rch"] = rch
m_ss["oc" ] = oc
m_ss["pcg"] = pcg
m_ss["gcg"] = gcg
m_ss["wel"] = wel
m_ss["drn"] = drn

m_ss.create_time_discretization(additional_times=["2014-12-31T23:59:59.000000000",
 "2035-01-01T00:00:00.000000000"]
)
m_ss["time_discretization"].dataset["transient"] = False
modeldir_ss = pathlib.Path("SS_1")
m_ss.write(modeldir_ss, result_dir = "data/4-output")

# additional_times = pd.date_range("2000-01-01", "3000-01-01", freq="100Y")
# %%
