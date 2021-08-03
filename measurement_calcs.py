# Python script for calculating esr automatically from traces
import pandas as pd
import numpy as np
import sys
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
shunt = 4.7
gain = 88
REBOUND_SECS = 0.5
SPACING = 10
LOW_LIM = 0.006
RISE_LIM = 0.02
FALL_LIM = 0.02
HIGH_LIM = 10

limTable = {
	'5':  [0.031, 0.031],
	'10': [0.015, 0.015],
	'25': [0.023, 0.025],
	'50': [0.05, 0.05]

}


timeScaling = 125e3
startTime = 0  
endTime = -1

eff_table = {2.4 : { .0001: .45, .0002:.60, .0003:.65,.0005:.70,
.001:.75, .002: .78, .004:.79, .006:.79,.008:.80, .015:.80, .02:.81,
.03:.82,.1:.84,.2:.85,.6:.85},
1.8 : { .0001: .45, .0002:.55, .0003:.6,.0005:.65, .001:.70, .002: .72, .004:.74,
.006:.75,.008:.76, .015:.76, .02:.76, .03:.76,.1:.77,.2:.83,.4:.81},
.9: { .0001: .35, .0002:.42, .0003:.46,.0005:.5, .001:.52, .002: .53, .004:.54,
.006:.55,.008:.57, .015:.57, .02:.58, .03:.6,.1:.75,.15:.70,.2:.6}
}

voltsPerLSB = 4.88

def convertToV( adcReading ):
  adc_max = 4095
  v_max = 5.2394959999999999 
  v_min = -0.34275899999999998  
  return np.add( np.multiply( np.true_divide( adcReading, adc_max ), v_max - v_min ), v_min )

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


def extract_first_dip(first_deriv,times_decimated,lim=.025):
  start = -1
  stop = -1
  #lim = .01
  time_start = -1
  for i, x in enumerate(first_deriv):
    if start == -1:
      if x < -1*lim:
        start = i
    else:
      if x > lim:
        stop = i
        time_start = times_decimated[start]
        start = -1
        stop = -1
        break
  return time_start


def plot_two(filename, filename1,spacing=100,lim=.01):
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  vcaps = vals[:,1]
  times = vals[:,0]
  vcaps_decimated = vcaps[::spacing]
  times_decimated = times[::spacing]
  first_deriv = np.diff(vcaps_decimated)
  try:
    df = pd.read_csv(filename1, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename1, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals1 = df.values
  vcaps1 = vals1[:,1]
  times1 = vals1[:,0]
  vcaps_decimated1 = vcaps1[::spacing]
  times_decimated1 = times1[::spacing]
  first_deriv1 = np.diff(vcaps_decimated1)
  # Find first peak in first input
  time_start = extract_first_dip(first_deriv,times_decimated)
  # Find first peak in second input
  time_start1 = extract_first_dip(first_deriv1,times_decimated1)

  fig, ax = plt.subplots()
  ax.plot(times_decimated, vcaps_decimated,'b',times_decimated1,vcaps_decimated1,'r')
  #ax.plot(times_decimated1, vcaps_decimated1,'r-')
  plt.show()

def find_min(filename,load,spacing=100,limFall=.01,limRise=.02):
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  
  vcaps = vals[startTime:endTime,1]
  times = vals[startTime:endTime,0]
  
  if vcaps[0] > 5:
  	vcaps = convertToV( vcaps )
  
  vcaps_decimated = vcaps[::spacing]
  times_decimated = times[::spacing]
  first_deriv = np.diff(vcaps_decimated)
  # Find the start/stop points
  time_pairs = []
  index_pairs = []
  start = -1
  stop = -1
  #lim = .025
  #lim = .01
  esrs = []
  for i, x in enumerate(first_deriv):
    if start == -1:
      if x < -1*limFall:
        start = i
    else:
      if x > limRise:
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
    #print(pair[1],rebound_index)
    rebound_v = max(vcaps_decimated[pair[1]:rebound_index])
    esr = (rebound_v - min_v)/load
    esrs.append(esr)
    print("Esr is: ",esr, "measured for times: ",\
    times_decimated[pair[0]], \
    times_decimated[pair[1]], "|")
    E_used = load*np.multiply(vcaps_decimated[pair[0]:pair[1]],times_decimated[1]
    -times_decimated[0])
    #print("E_used is ",np.sum(E_used))
  print(esrs)
  fig, ax = plt.subplots()
  ax.plot(times_decimated, vcaps_decimated,'b-')
  #print(len(times_decimated),len(first_deriv[::spacing]))
  ax2 = ax.twinx()
  ax2.plot(times_decimated[1:],first_deriv,'k.')
  ax2.hlines( [-1*limFall, limRise], times_decimated[0], times_decimated[-1], colors=['red', 'red'] )
  plt.show()
  return np.average(esrs)
  #fig, ax = plt.subplots()
  #cap_current = first_deriv*.045/(times_decimated[1] - times_decimated[0])
  #ax.plot(times_decimated[1:], cap_current,'r')
  #plt.show()

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
  num_files = len(sys.argv)
  #print(len (sys.argv))
  i = 1
  all_files = []
  while i < num_files:
    #print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  #all_files = glob.escape(all_files)
  esr_vals = []
  for filename in all_files:
    #pos = re.search('_10s_',filename).start()
    pos = re.search('mA_',filename).start()
    load_str = filename[:pos]
    pos = re.search('vcap_',load_str).end()
    load_str = load_str[pos:]
    #print(load_str)
    loads = re.findall(r'[0-9]+',load_str)
    #print(loads)
    load = float(loads[1])
    load = load*1e-3
    print("Running with load %s mA" % (1000*load))
    spacing = SPACING
    #spacing = 500
    if (load < .010):
      spacing = 1000
    #pos = re.search('_10s_',filename).end()
    pos = re.search('mA_',filename).end()
    end_str = filename[pos:]
    pos = re.search('_duty_cycle',end_str).start()
    end_str = end_str[:pos]
    secs = re.findall(r'[0-9]+',end_str)
    #print('Filename end: %s' % end_str)
    #print(secs)
    base = float(secs[0])
    #print("Base is: ",base)
    if len(secs) > 2:
      if (float(secs[2]) < 10):
        sec_dec = float(secs[2])*10
      else:
        sec_dec = float(secs[2])
      sec_dec *= .01
    else:
      sec_dec = 0
    #print("Sec dec is: ",sec_dec)
    #print("Sec is",secs[1])
    duty_cycle = float(secs[1]) + sec_dec
    print("duty cycle is: ",duty_cycle)
    on_time = base - .01*duty_cycle*base
    print("on time is ",on_time)
    if on_time <= .01:
      limRise = limTable[str(int(1000*load))][0]
      limFall = limTable[str(int(1000*load))][1]
      spacing = 10
    else:
      limRise = limTable[str(int(1000*load))][0]
      limFall = limTable[str(int(1000*load))][1]
    print("lims are: %s[Rise], %s[Fall]" % (limRise, limFall))
    avg_esr = find_min(filename,load,spacing,limRise, limFall)
    if np.isnan(avg_esr) == False:
      esr_vals.append(avg_esr)
    print("Avg esr is: ",avg_esr)
  print("Done! ESRs are ", esr_vals)
  print(all_files)
  #esr_vals = esr_vals[~np.isnan(esr_vals)]
  print("Final avg is: ", np.average(esr_vals), "for runtime ", on_time)
  sys.exit()
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
