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
import glob

all_files = []
real_mins = []
meas_mins = []

eff = [.8,.73,.56]
vi = [2.4,1.8,.9]
Voff = 1.6
Vrange = 3.3

USE_REAL = 1
DEGREE = 1
SEC_PER_SAMPLE = .001
RUN_SHORT = 0

mv_off = []

def calc_vsafe(Vs,Vmin,Vf):
  m,b= np.polyfit(vi,eff,1)
  print("m,b:",m,b)
  const = (m*Vs**3)/3 + (b*Vs**2)/2 - (m*Vf**3)/3 - (b*Vf**2)/2 + \
    (m*Voff**3)/3 + (b*Voff**2)/2
  p = [m/3,b/2,0,-1*const]
  V_e = np.roots(p)
  Vd = (Vf - Vmin)
  scale = Vmin*(m*Vmin+b)/(Voff*(m*Voff + b))
  Vd_new = Vd*scale
  reals = V_e[np.isreal(V_e)][0]
  Vsafe = reals.real + Vd_new
  guess = Vs**2 + Voff**2 - Vf**2
  guess = guess**(1/2)
  f_guess = (m/3)*guess**3 + (b/2)*guess**2 - const
  f_prime_guess = m*guess**2 + b*guess
  approx = guess - f_guess/f_prime_guess
  print("Vsafe: ",reals.real, "approx:",approx,"Diff:",reals.real - approx)
  n_voff = m*Voff + b
  n_vs = m*Vs + b
  new_guess = (n_vs/n_voff)*(Vs**2 - Vf**2) + Voff**2
  new_guess = new_guess**(1/2)
  print("\tEasy guess:",new_guess,"diff:",reals.real-new_guess)
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
  clipped_min = np.average(clipped[0:100,4])
  meas_mins = vals[vals[:,0] < time]
  step = int(np.floor(SEC_PER_SAMPLE/(vals[1,0] - vals[0,0])))
  print("Step is: ",step,vals[1,0] - vals[0,0])
  meas_min = np.min(meas_mins[::step,4])
  print("True meas min vs clipped",meas_min,clipped_min)
  return [meas_min,real_min,vstart,vfinal]

def phase_process(filename):
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
  clipped_min = np.average(clipped[0:100,4])
  meas_mins = vals[vals[:,0] < time]
  step = int(np.floor(SEC_PER_SAMPLE/(vals[1,0] - vals[0,0])))
  mins = []
  for phase in np.arange(0,step,int(step/100)):
    mins.append(np.min(meas_mins[phase::step,4]))
  print("\tStd dev is:",np.std(mins))


if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  real_vsafes = pickle.load(open("brute_force_vstarts.pkl","rb"))
  while i < num_files:
    #print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  if RUN_SHORT:
    for filename in all_files:
      print(filename)
      #phase_process(filename)
      #continue
      [mm, rm, vs,vf] = process_file(filename)
      # Goofy switcheroo, not sure if we need it yet
      real_mins.append(rm)
      meas_mins.append(mm)
  #sys.exit(0)
  #print(real_mins)
  #print(meas_mins)
  if USE_REAL != 1:
    if DEGREE == 2:
      fit = np.polyfit(meas_mins,real_mins,2,full=True)
    else:
      fit = np.polyfit(meas_mins,real_mins,1,full=True)
    results_file = open("fit_"+ str(DEGREE) +"_"+str(SEC_PER_SAMPLE)+".pkl","wb")
    pickle.dump(fit,results_file)
    results_file.close()
    sse = fit[1][0]
    diff = np.subtract(real_mins,np.mean(real_mins))
    diff = diff**2
    sst = np.sum(diff)
    r2 = 1 - sse/sst
    if DEGREE == 2:
      print("Fit is: ",r2,"m^2, m, b are",fit[0][0],fit[0][1],fit[0][2])
    else:
      print("Fit is: ",r2,"m,b are",fit[0][0],fit[0][1])
    sys.exit(0)
  for filename in all_files:
    print(filename)
    pos = re.search('EXT',filename).start()
    base_name = filename[pos:]
    numbers = re.findall(r'[0-9]+',base_name)
    expt_id = int(numbers[0])
    #print("Expt id: ",expt_id)
    [mm, rm, vs, vf] = process_file(filename)
    if USE_REAL != 1:
      if DEGREE == 2:
        est_m = (mm**2)*fit[0][0] + mm*fit[0][1] + fit[0][2]
      else:
        est_m = mm*fit[0][0] + fit[0][1]
      expt_range = vs - rm
      print("Range is:",expt_range,vs,rm,mm,"Min diff is: ",\
      math.trunc(100*(est_m - rm)/expt_range),est_m,rm)
      print("full diff: ",est_m-rm,math.trunc(100*(est_m - rm)/(2.5-1.6)))
    #print("Vf is: ",vf,"Est m is", est_m)
    if USE_REAL:
      vsafe = calc_vsafe(vs,rm,vf)
    else:
      vsafe = calc_vsafe(vs,est_m,vf)
    if expt_id in real_vsafes:
      print(expt_id,"Vsafes: Est:",vsafe,"Real:",real_vsafes[expt_id])
      print("\t\t",math.trunc(100*(vsafe - real_vsafes[expt_id])/(2.5-1.6)))
      mv_off.append(vsafe - real_vsafes[expt_id])
    else:
      print("No id match:",expt_id,"Est:",vsafe)

  print("Average mm off: ",np.average(mv_off))
