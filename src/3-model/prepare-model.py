""" Here the model is prepared. Time discretization can be adjusted to 1s to retrieve SS results
"""
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
drn2= imod.wq.Drainage.from_file("data/3-input/drn_2.nc")
drn3= imod.wq.Drainage.from_file("data/3-input/drn_3.nc")
chd = imod.wq.ConstantHead.from_file("data/3-input/chd.nc")
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
m_ss["drn"]  = drn
m_ss["drn2"] = drn2
m_ss["drn3"] = drn3
m_ss["chd"]  = chd
#m_ss["riv"] = riv
#%%
m_ss.create_time_discretization(additional_times=[
    "2014-12-31T23:59:59.000000000", "2015-01-01T00:00:00.000000000","2020-01-01T00:00:00.000000000","2025-01-01T00:00:00.000000000",
    "2030-01-01T00:00:00.000000000", "2035-01-01T00:00:00.000000000","2040-01-01T00:00:00.000000000","2045-01-01T00:00:00.000000000",
    "2050-01-01T00:00:00.000000000", "2055-01-01T00:00:00.000000000","2060-01-01T00:00:00.000000000","2065-01-01T00:00:00.000000000","2070-01-01T00:00:00.000000000",
    "2075-01-01T00:00:00.000000000", "2080-01-01T00:00:00.000000000","2085-01-01T00:00:00.000000000","2090-01-01T00:00:00.000000000","2095-01-01T00:00:00.000000000",
    "2100-01-01T00:00:00.000000000", "2105-01-01T00:00:00.000000000","2110-01-01T00:00:00.000000000","2115-01-01T00:00:00.000000000",
    "2120-01-01T00:00:00.000000000", "2125-01-01T00:00:00.000000000","2130-01-01T00:00:00.000000000","2135-01-01T00:00:00.000000000", 
    "2140-01-01T00:00:00.000000000", "2145-01-01T00:00:00.000000000","2150-01-01T00:00:00.000000000","2155-01-01T00:00:00.000000000", 
    "2160-01-01T00:00:00.000000000", "2165-01-01T00:00:00.000000000","2170-01-01T00:00:00.000000000","2175-01-01T00:00:00.000000000", 
    "2180-01-01T00:00:00.000000000", "2185-01-01T00:00:00.000000000","2190-01-01T00:00:00.000000000","2195-01-01T00:00:00.000000000",
    "2200-01-01T00:00:00.000000000", "2205-01-01T00:00:00.000000000","2210-01-01T00:00:00.000000000","2215-01-01T00:00:00.000000000",]
)
m_ss["time_discretization"].dataset["transient"] = False
modeldir_ss = pathlib.Path("data/3-input/SS_1")
m_ss.write(modeldir_ss, result_dir = "data/4-output")

# additional_times = pd.date_range("2000-01-01", "3000-01-01", freq="100Y")
# %%
