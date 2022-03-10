# Script for processing the outputs of the meas_min experiments that use extra
# circuitry to try to pin the minimum in hardware so we don't have to repeatedly
# read the damn thing in software

import pandas as pd
import numpy as np
import sys
import matplotlib
import pickle
import re
import math

all_files = []
real_mins = []
meas_mins = []

eff = [.8,.73,.56]
vi = [2.4,1.8,.9]
Voff = 1.6
Vrange = 3.3

USE_REAL = 1

def calc_vsafe(Vs,Vmin,Vf):
  m,b= np.polyfit(vi,eff,1)
  const = (m*Vs**3)/3 + (b*Vs**2)/2 - (m*Vf**3)/3 - (b*Vf**2)/2 + \
    (m*Voff**3)/3 + (b*Voff**2)/2
  p = [m/3,b/2,0,-1*const]
  V_e = np.roots(p)
  Vd = (Vf - Vmin)
  scale = Vmin*(m*Vmin+b)/(Voff*(m*Voff + b))
  Vd_new = Vd*scale
  reals = V_e[np.isreal(V_e)][0]
  Vsafe = reals.real + Vd_new
  #print("Vsafe: ",Vsafe)
  return Vsafe


def process_file(filename):
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  vcaps = vals[vals[:,0] > 0]
  vstart = np.average(vals[0:100,1])
  stop_times = vals[:,9:11]
  stop_time = stop_times[stop_times[:,1] == 0]
  stop_time = stop_time[-1,0]
  #print("Stop_time ",stop_time)
  real_min = min(vcaps[:,1])
  vcaps = vals[vals[:,0] > (stop_time)]
  vfinal = np.average(vcaps[0:100,1])
  meas_times = vals[:,5:7]
  meas_times = meas_times[meas_times[:,1] > 0]
  time = meas_times[-2,0]
  clipped = vals[vals[:,0] > time]
  meas_min = np.average(clipped[0:100,4])
  return [meas_min,real_min,vstart,vfinal]


if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  real_vsafes = pickle.load(open("brute_force_vstarts.pkl","rb"))
  while i < num_files:
    #print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    [mm, rm, vs,vf] = process_file(filename)
    # Goofy switcheroo, not sure if we need it yet
    real_mins.append(rm)
    meas_mins.append(mm)
  #print(real_mins)
  #print(meas_mins)
  fit = np.polyfit(meas_mins,real_mins,1,full=True)
  sse = fit[1][0]
  diff = np.subtract(real_mins,np.mean(real_mins))
  diff = diff**2
  sst = np.sum(diff)
  r2 = 1 - sse/sst
  #print("Fit is: ",r2,"m,b are",fit[0][0],fit[0][1])
  for filename in all_files:
    pos = re.search('EXT',filename).start()
    base_name = filename[pos:]
    numbers = re.findall(r'[0-9]+',base_name)
    expt_id = int(numbers[0])
    #print("Expt id: ",expt_id)
    [mm, rm, vs, vf] = process_file(filename)
    est_m = mm*fit[0][0] + fit[0][1]
    #print("Vf is: ",vf,"Est m is", est_m)
    if USE_REAL:
      vsafe = calc_vsafe(vs,rm,vf)
    else:
      vsafe = calc_vsafe(vs,est_m,vf)
    if expt_id in real_vsafes:
      print(expt_id,"Est:",vsafe,"Real:",real_vsafes[expt_id])
      print("\t",math.trunc(100*(vsafe - real_vsafes[expt_id])/(2.5-1.6)))
    else:
      print("No id match:",expt_id,"Est:",vsafe)


