# Python script for generating Vsafes
import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import re
shunt = 4.7
gain = 88
REBOUND_SECS = 3

eff_table = {2.4 : { .0001: .45, .0002:.60, .0003:.65,.0005:.70,
.001:.75, .002: .78, .004:.79, .006:.79,.008:.80, .015:.80, .02:.81,
.03:.82,.1:.84,.2:.85,.6:.85},
1.8 : { .0001: .45, .0002:.55, .0003:.6,.0005:.65, .001:.70, .002: .72, .004:.74,
.006:.75,.008:.76, .015:.76, .02:.76, .03:.76,.1:.77,.2:.83,.4:.81},
.9: { .0001: .35, .0002:.42, .0003:.46,.0005:.5, .001:.52, .002: .53, .004:.54,
.006:.55,.008:.57, .015:.57, .02:.58, .03:.6,.1:.75,.15:.70,.2:.6}
}

def calc_esr(load,start_V,min_V,stop_V):
  esr = (stop_V - min_V)/load
  v_drop = start_V-esr*load
  #print("%.2f" % load,"%.2f" % start_V,"%.2f" % min_V,"%.2f" % stop_V, ": ")
  #print("\t esr: ","{:%.f}".format(esr)," V after drop:","{:%.f}".format(v_drop))
  print("%.2f" % esr, "%.2f" % v_drop)
def calc_esr_batch(filename):
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  i = 0;
  while i < vals.shape[0]:
    calc_esr(vals[i,0],vals[i,1],vals[i,2],vals[i,3])
    i += 1

def find_nearest(array,value):
  new_array = np.asarray(array)
  new_arr = new_array - value
  new_new_arr = np.absolute(new_arr)
  idx = new_new_arr.argmin()
  return array[idx]

def find_nearest_idx(array,value):
  new_array = np.asarray(array)
  new_arr = new_array - value
  new_new_arr = np.absolute(new_arr)
  idx = new_new_arr.argmin()
  return idx


def get_eff(V_in,I_out,eff):
  V = find_nearest([*eff.keys()],V_in)
  I = find_nearest([*eff[V].keys()],I_out)
  return eff[V][I]


def find_min(filename,load):
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  vcaps = vals[:,1]
  times = vals[:,0]
  vcaps_decimated = vcaps[::100]
  times_decimated = times[::100]
  first_deriv = np.diff(vcaps_decimated)
  # Find the start/stop points
  time_pairs = []
  index_pairs = []
  start = -1
  stop = -1
  for i, x in enumerate(first_deriv):
    if start == -1:
      #if x < -.1:
      if x < -.025:
        start = i
    else:
      #if x > .1:
      if x > .025:
        stop = i
        time_pairs.append([times_decimated[start],times_decimated[stop]])
        index_pairs.append([start,stop])
        start = -1
        stop = -1
  print(time_pairs)
  print(index_pairs)
  for i, pair in enumerate(index_pairs):
    print(i,pair)
    min_v = min(vcaps_decimated[pair[0]:pair[1]])
    rebound_time = time_pairs[i][1] + REBOUND_SECS
    if (rebound_time > max(times_decimated)):
      continue
    rebound_index = find_nearest_idx(times_decimated,rebound_time)
    print(pair[1],rebound_index)
    rebound_v = max(vcaps_decimated[pair[1]:rebound_index])
    esr = (rebound_v - min_v)/load
    print("Esr is: ",esr)
  fig, ax = plt.subplots()
  ax.plot(times_decimated, vcaps_decimated,'b.')
  print(len(times_decimated),len(first_deriv[::100]))
  ax2 = ax.twinx()
  ax2.plot(times_decimated[1:],first_deriv,'k.')
  plt.show()

# Load levels, in A
loads = [5.4e-3, 11.5e-3, 48e-3]

# Use 5 high esr cap power system (all in parallel)
cap_count = 6
#esr = 25/cap_count
esr = 37 # As measured
C = cap_count*7.5e-3
Vout = 2.5
#E_match = 0.005 # 100mA*2.5V*20ms (with perfect efficiency)
#E_match = 0.001
E_match = .00005 # 50mA*2.5V*4ms (with perfect efficiency)
#Vmin = 1.8
# Starting to work in separate thresholds for extreme and normal
Vmin  = .6
Vstart = 2.8

cont_runtimes = []
if __name__ == "__main__":
  # For stable voltages, here's how we calculate runtime:
  for load in loads:
    eff_load = load/get_eff(Vmin,load,eff_table)
    P_used = (Vout*eff_load)
    runtime = E_match/P_used
    Vdrop = esr*eff_load
    Vsafe = np.sqrt((Vmin + Vdrop)**2 + 2*E_match/C)
    adc =  4096*Vsafe/3.3
    print("Runtime for ",load,"mA is",runtime,"seconds, and vsafe is ",Vsafe,\
    " adc val is: ", adc)
