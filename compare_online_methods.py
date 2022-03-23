# Script to compare the energy and accuracy of several online approaches for
# estimating Vsafe

import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import pickle
import re
import math
import glob

eff = [.8,.73,.56]
vi = [2.4,1.8,.9]
Voff = 1.6
Vrange = 3.3
R_SHUNT = 4.7
GAIN = 16
Vdd = 2.56

BRUTE_FORCE_PATH = "brute_force_vstarts.pkl"
# We generated the model with runs from 03-17 *after* 21:00, so use something
# different to test
#TODO generate the secs per sample and degree from the model name
MEAS_MIN_MODEL = "fit_1_0.05.pkl"
DEGREE = 1
SEC_PER_SAMPLE = .05


def culpeo_rt_vsafe(Vs,Vmin,Vf,opt=0):
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
  if opt == 0:
    return Vsafe
  elif opt == 1:
    return Vd_new
  elif opt == 2:
    return reals.real


def catnap_vsafe(Vs,Vmin,Vf):
  catnap_E = (Vs**2 - Vf**2)
  catnap_Vsafe = np.sqrt(catnap_E + Voff**2)
  return catnap_Vsafe;

estimates = {}
sampling_times = [.1, .05, .01, .005, .001]

# Needs to already be pruned
def calc_energy(vals):
  Is = vals[vals[:,0] > 0]
  stops = vals[:,5:7]
  stops = stops[stops[:,1] == 1]
  print(stops)
  stop = stops[0,0]
  print(stop)
  Is = Is[Is[:,0] < stop]
  diffs = np.subtract(Is[:,1],Is[:,2])
  if any(diff < 0 for diff in diffs):
    print("flipping!\r\n");
    diffs = np.subtract(Is[:,2],Is[:,1])
  new_I = np.divide(diffs,R_SHUNT*GAIN)
  print(new_I)
  P = np.multiply(new_I,Vdd)
  E_deltas = np.multiply(P,vals[1,0] - vals[0,0])
  E = np.sum(E_deltas)
  return(E)

  

def get_vals(filename,secs_per_sample):
  pos = re.search('EXT',filename)
  if pos != None:
    pos = pos.start()
  else:
    pos = re.search('EXPT',filename).start()
  base_name = filename[pos:]
  numbers = re.findall(r'[0-9]+',base_name)
  expt_id = int(numbers[0])
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  step = int(np.floor(secs_per_sample/(vals[1,0] - vals[0,0])))
  vcaps = vals[vals[:,0] > 0]
  vstart = np.average(vals[0:100,1])
  stop_times = vals[:,9:11]
  catnap_stops = stop_times[stop_times[:,1] == 1]
  catnap_stop = stop_times[1,0]
  energy = calc_energy(vals)
  print("Energy is: ",energy)
  return [0,0,0,0,0,0]  #TODO take this out
  vcaps_catnap = vals[vals[:,0] > catnap_stop]
  catnap_final = np.average(vals[0:100,1])
  stop_time = stop_times[stop_times[:,1] == 0]
  stop_time = stop_time[-1,0]
  vcaps_temp = vals[vals[:,0] < stop_time]
  vcap_min = np.min(vcaps_temp[::step,1])
  vcaps = vals[vals[:,0] > (stop_time)]
  vfinal = np.average(vcaps[0:100,1])
  meas_times = vals[:,5:7]
  meas_times = meas_times[meas_times[:,1] > 0]
  time = meas_times[-2,0]
  clipped = vals[vals[:,0] > time]
  clipped_min = np.average(clipped[0:100,4])
  meas_mins = vals[vals[:,0] < time]
  meas_min = np.min(meas_mins[::step,4])
  return [expt_id,meas_min,vcap_min,vstart,vfinal,catnap_final]

def get_est_min(mm,degree,secs):
  if degree == 2:
    est_m = (mm**2)*fit[0][0] + mm*fit[0][1] + fit[0][2]
  else:
    est_m = mm*fit[0][0] + fit[0][1]
  return est_m

symbols = {.1:'v',.05:'s',.01:'p',.005:'h',.001:'o'}
symbols2 = {.1:'.',.05:'_',.01:'1',.005:'x',.001:'+'}
colors = {'catnap':'b','vcap':'r','vmeas_min':'g'}
def plot_comparison():
  # Plot bar chart(?) Comparing accuracy at different sampling levels across
  # experiments
  # grouping is estimator, bars are expts
  plot_estimates = pickle.load(open("test.pkl","rb"))
  fig = plt.figure()
  fig1 = plt.figure()
  ax = fig.add_subplot(111)
  ax1 = fig1.add_subplot(111)
  for sys in plot_estimates.keys():
    sys_count = {.1:0,.05:0,.01:0,.005:0,.001:0}
    for expt in plot_estimates[sys].keys():
      for secs in plot_estimates[sys][expt].keys():
        diff = 0
        count = 0
        ests = []
        for est in plot_estimates[sys][expt][secs]:
          diff += est - real_vsafes[expt]
          count += 1
          ests.append(est)
        diff = diff/count
        if sys == 'catnap':
          samples = 0
        else:
          samples = 1/secs
        if diff < 0:
          sys_count[secs] += 1
          print("Expt: ",expt,"diff: ",diff,"freq:",samples,"sys:",sys)
          print("\tReal:",real_vsafes[expt],"vs:",ests)
        ax.scatter(expt,diff,marker=symbols[secs],c=colors[sys])
        ax1.scatter(samples,diff,c=colors[sys],marker=symbols2[secs])
    print("Total off: ",sys_count,"sys",sys)
  plt.legend()
  ax.axhline(0)
  ax1.axhline(0)
  fig.savefig('acc_scatter_plot.pdf',format='pdf',bbox_inches='tight')
  fig1.savefig('acc_by_sampling_plot.pdf',format='pdf',bbox_inches='tight')




def run_compare_online(all_files):
  for filename in all_files:
    #print(filename)
    for secs in sampling_times:
      #print("\t",secs)
      results = get_vals(filename,secs)
      expt = results[0]
      #print("Keys:",estimates["catnap"].keys(),\
      #not(expt in estimates["catnap"].keys()))
      if not(expt in estimates["catnap"].keys()):
        #print("Add expt",expt)
        estimates["catnap"][expt] = {}
        estimates["vcap"][expt] = {}
        estimates["vmeas_min"][expt] = {}
      if not(secs in estimates["catnap"][expt].keys()):
        #print("Add secs",expt,secs)
        estimates["catnap"][expt][secs] = []
        estimates["vcap"][expt][secs] = []
        estimates["vmeas_min"][expt][secs] = []
      meas_min = results[1]
      vcap_min = results[2]
      vstart = results[3]
      vfinal = results[4]
      vfinal_short = results[5]
      # TODO this doesn't change with sampling, move it outside
      estimates["catnap"][expt][secs].append(catnap_vsafe(vstart,vcap_min,vfinal_short))
      estimates["vcap"][expt][secs].append(culpeo_rt_vsafe(vstart,vcap_min,vfinal))
      est_min = get_est_min(meas_min,DEGREE,secs)
      estimates["vmeas_min"][expt][secs].append(culpeo_rt_vsafe(vstart,est_min,vfinal))
      #print(estimates)
  #print(estimates)
  results_file = open("estimates_" + str(DEGREE) + "_" + str(SEC_PER_SAMPLE )+ \
  ".pkl","wb")
  pickle.dump(estimates,results_file)
  results_file.close()

class event:
  def __init__(self,vstart,vsafe,vdrop,V_final_catnap=0):
    self.Vstart = vstart
    self.Vsafe = vsafe
    self.Vdrop = vdrop
    self.Vfc = V_final_catnap
  def transfer_vsafe(self,Vb):
    vb_sq =  self.Vstart**2 -self.Vsafe**2 + Voff**2
    return vb_sq**(1/2)
  def transfer_catnap(self,Vcb):
    vbc_sq = Vcb**2 + self.Vsafe**2 - self.Vfc**2
    return vbc_sq**(1/2)

# Returns culpeo vbucket, then catnap vbucket
def calc_vbucket(events):
  #Vb = events[-1].Vsafe # start vbucket
  Vb = 0
  Vcb = Voff
  events = np.flip(events)
  for i, ev in enumerate(events):
    if (Vb - ev.Vdrop > Voff):
      Vb = Voff + ev.Vdrop
    Vb = ev.transfer_vsafe(Vb) # tranfser with drop
    Vcb = ev.transfer_catnap(Vcb) # transfer w/out drop
  return [Vb,Vcb]


# Assumes that you've fed in files for events that need to happen in order with
# no incoming energy
def process_event_bucket(files):
  events = []
  for filename in all_files:
    results = get_vals(filename,.001)
    print("Vsafe is: ",real_vsafes[results[0]])
    vcap_min = results[2]
    vfinal = results[4]
    vstart = results[3]
    vdrop = vfinal - vcap_min
    vsafe = culpeo_rt_vsafe(vstart,vcap_min,vfinal,opt=2)
    vdrop = culpeo_rt_vsafe(vstart,vcap_min,vfinal,opt=1)
    events.append(event(vstart,vsafe,vdrop))
  Vb = calc_vbucket(events)
  print("Bucket level is: ",Vb)



if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  real_vsafes = pickle.load(open(BRUTE_FORCE_PATH,"rb"))
  estimates["catnap"] = {}
  estimates["vcap"] = {}
  estimates["vmeas_min"] = {}
  while i < num_files:
    all_files.append(sys.argv[i])
    i += 1
  fit_files = glob.glob("./fit_*.pkl")
  if num_files < 5:
    process_event_bucket(all_files)
    sys.exit(0)
  if num_files < 10:
    for filename in all_files:
      print(filename)
      get_vals(filename,.001)
    sys.exit(0)
  for filename in fit_files:
    print(filename)
    MEAS_MIN_MODEL = filename
    fit = pickle.load(open(MEAS_MIN_MODEL,"rb"))
    pos = re.search('fit',filename).start()
    base_name = filename[pos:]
    numbers = re.findall(r'[0-9]+',base_name)
    DEGREE = int(numbers[0])
    print(DEGREE)
    SEC_PER_SAMPLE = int(numbers[2])/100
    print(SEC_PER_SAMPLE)
    run_compare_online(all_files)

    plot_comparison()
