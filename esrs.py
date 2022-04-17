# This script outputs safe voltages, it analyzes current traces to do it
# it actually has nothing to do with esr calculations... like at all

import min_voltage_notes as minV
import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import re
import glob
import pickle
import meas_min_process as mmmp

DO_PLOT = False
#V_RANGE = 2.485
V_RANGE = 3.3
V_MIN = 1.6
CAP_VAL = 45e-3
EFF_VMIN = .5
#CAP_VAL = 63e-3
#Offset in seconds:
#TIME_OFFSET = .002
TIME_OFFSET = .000263
TIME_OFFSET_lucky = 0
TIME_OFFSET_unlucky = .1
TIME_OFFSET_energy = 0.500

DYN_SEC_PER_SAMPLE = .001
HW_SEC_PER_SAMPLE = .00001

esrs = {
1000: 34.13,
100: 21.59,
10: 8.689,
1: 3.226
}

times = {
  1000: 1,
  100: .1,
  10: .01087,
  1: .00187,
  200: .2,
  110: .11,
  101: .101,
}


esrs_by_id = {
1: esrs[1000],
2: esrs[1000],
3: esrs[100],
4: esrs[100],
5: esrs[100],
6: esrs[10],
7: esrs[10],
8: esrs[10],
9: esrs[10],
10: esrs[1],
11: esrs[1],
12: esrs[1],
13: esrs[1000],
14: esrs[1000],
15: esrs[100],
16: esrs[100],
17: esrs[100],
18: esrs[10],
19: esrs[10],
20: esrs[10],
21: esrs[10],
22: esrs[1],
23: esrs[1],
24: esrs[1],
25: esrs[1000],
26: esrs[1000],
27: esrs[100],
28: esrs[100],
29: esrs[100],
30: esrs[10],
31: esrs[10],
32: esrs[10],
33: esrs[10],
34: esrs[1],
35: esrs[1],
36: esrs[1],
};


time_by_id = {
1: times[1000],
2: times[1000],
3: times[100],
4: times[100],
5: times[100],
6: times[10],
7: times[10],
8: times[10],
9: times[10],
10: times[1],
11: times[1],
12: times[1],
13: times[1000],
14: times[1000],
15: times[200],
16: times[200],
17: times[200],
18: times[110],
19: times[110],
20: times[110],
21: times[110],
22: times[101],
23: times[101],
24: times[101],
25: times[1000],
26: times[1000],
27: times[200],
28: times[200],
29: times[200],
30: times[110],
31: times[110],
32: times[110],
33: times[110],
34: times[101],
35: times[101],
36: times[101],
}

def make_adc_file_str(expt_id, val):
  adc = np.ceil(4096*val/V_RANGE)
  adc_val = int(adc)
  file_str = "#define VSAFE_ID" + str(expt_id) + " " + str(adc_val) + "\n"
  return file_str

def make_adc_val(val):
  adc = np.ceil(4096*val/V_RANGE)
  adc_val = int(adc)
  return adc_val

catnap_vals = {}
lucky_vals = {}
unlucky_vals = {}
culpeo_vals = {}
energy_vals = {}
dynamic_vals = {}
hardware_vals = {}

if __name__ == "__main__":
#og culpeo static
  file_str = "culpeo_" + str(V_MIN) + "_" + str(CAP_VAL)
  esr_file = open(file_str,"w")
# catnap realistic
  file_str = "catnap_" + str(V_MIN) + "_" + str(CAP_VAL)
  catnap_file = open(file_str,"w")
# catnap lucky
  file_str = "lucky_" + str(V_MIN) + "_" + str(CAP_VAL)
  lucky_file = open(file_str,"w")
# catanp unlucky
  file_str = "unlucky_" + str(V_MIN) + "_" + str(CAP_VAL)
  unlucky_file = open(file_str,"w")
# energy
  file_str = "energy_" + str(V_MIN) + "_" + str(CAP_VAL)
  energy_file = open(file_str,"w")
# dynamic
  file_str = "dynamic_" + str(V_MIN) + "_" + str(CAP_VAL)
  dynamic_file = open(file_str,"w")
# hardware
  file_str = "hardware_" + str(V_MIN) + "_" + str(CAP_VAL)
  hardware_file = open(file_str,"w")
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    if len(re.findall('fail',filename)) > 0:
      continue
    expt_id = int(re.findall(r'[0-9]+',filename)[0])
    print("Expt id is ",expt_id)
    minV.CAP_ESR=esrs_by_id[expt_id];
    # Set conditions
    #minV.CAP = 23e-3
    #minV.CAP = 64e-3
    minV.CAP = CAP_VAL
    minV.gain = 16
    minV.shunt = 4.7
    minV.MIN_VOLTAGE = V_MIN
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals = df.values
    # Drop time before 1s
    # Not needed for new version
    all_vals = vals
    if (expt_id < 13):
      vals = vals[vals[:,0]>1.2]
      all_vals = vals
      vals = vals[vals[:,0]<1.3 + time_by_id[expt_id]+TIME_OFFSET]
      print("End = ",1.3 + time_by_id[expt_id] + TIME_OFFSET)
    else:
      vals = vals[vals[:,0]< time_by_id[expt_id]+.010+TIME_OFFSET]
      print("End = ",time_by_id[expt_id] + .010 + TIME_OFFSET)
    diffs = np.subtract(vals[:,3],vals[:,2])
    if any(diff < 0 for diff in diffs):
      print("Upside down!")
      diffs = np.subtract(vals[:,2],vals[:,3])
    I = np.divide(diffs,minV.gain*minV.shunt)
    start_avg = np.average(vals[0:100,1])
    stop_avg = np.average(vals[-100:,1])
    print("Start stop: ",start_avg, stop_avg)
    if DO_PLOT == True:
      fig, ax = plt.subplots()
      ax.plot(vals[:,0],vals[:,1])
      plt.title("plot current")
      plt.show()
    #I = np.add(I,500e-6)
    # Various Vsafe calcs
    print("max I is:", max(I))
    dt = vals[1,0] - vals[0,0]
# Catnap realistic
    catnap_E = .5*CAP_VAL*(start_avg**2 - stop_avg**2)
    catnap_Vsafe = np.sqrt(2*catnap_E/CAP_VAL + V_MIN**2)
    print("\tCatnap vsafe is: ",catnap_Vsafe)
    catnap_vals[expt_id] = {make_adc_val(catnap_Vsafe)}
    catnap_file_str = make_adc_file_str(expt_id,catnap_Vsafe)
    ##----------------------------------------------------------
#Culpeo
    Vsafe = minV.calc_min_forward(I,dt,DO_PLOT)
    culpeo_vals[expt_id] = {make_adc_val(Vsafe)}
    Vsafe_culpeo_str = make_adc_file_str(expt_id,Vsafe)
    print("Expt ",expt_id," Vsafe is ",Vsafe)
    ##----------------------------------------------------------
#Lucky
    if (expt_id < 13):
      lucky_vals = all_vals[all_vals[:,0]<1.3 + \
      time_by_id[expt_id]+TIME_OFFSET_lucky]
      #print("End = ",1.3 + time_by_id[expt_id] + TIME_OFFSET)
    else:
      lucky_vals = all_vals[all_vals[:,0]< time_by_id[expt_id]+.010+TIME_OFFSET_lucky]
      #print("End = ",time_by_id[expt_id] + .010 + TIME_OFFSET)
    lucky_stop = np.average(lucky_vals[-100:,1])
    lucky = np.sqrt((start_avg**2 - lucky_stop**2) + V_MIN**2)
    lucky_vals[expt_id] = {make_adc_val(lucky)}
    lucky_str = make_adc_file_str(expt_id,lucky)
    print("lucky ",expt_id," Vsafe is ",lucky_vsafe)
    ##----------------------------------------------------------
#UnLucky
    if (expt_id < 13):
      unlucky_vals = all_vals[all_vals[:,0]<1.3 + \
      time_by_id[expt_id]+TIME_OFFSET_unlucky]
      #print("End = ",1.3 + time_by_id[expt_id] + TIME_OFFSET)
    else:
      unlucky_vals = all_vals[all_vals[:,0]< time_by_id[expt_id]+.010+TIME_OFFSET_unlucky]
      #print("End = ",time_by_id[expt_id] + .010 + TIME_OFFSET)
    unlucky_stop = np.average(unlucky_vals[-100:,1])
    unlucky = np.sqrt((start_avg**2 - unlucky_stop**2) + V_MIN**2)
    unlucky_str = make_adc_file_str(expt_id,unlucky)
    unlucky_vals[expt_id] = {make_adc_val(unlucky)}
    print("unlucky ",expt_id," Vsafe is ",unlucky_vsafe)
    ##----------------------------------------------------------
#Energy
    if (expt_id < 13):
      energy_vals = all_vals[all_vals[:,0]<1.3 + \
      time_by_id[expt_id]+TIME_OFFSET_energy]
      #print("End = ",1.3 + time_by_id[expt_id] + TIME_OFFSET)
    else:
      energy_vals = all_vals[all_vals[:,0]< time_by_id[expt_id]+.010+TIME_OFFSET_energy]
      #print("End = ",time_by_id[expt_id] + .010 + TIME_OFFSET)
    energy_stop = np.average(energy_vals[-100:,1])
    energy = np.sqrt((start_avg**2 - energy_stop**2) + V_MIN**2)
    energy_vals[expt_id] = {make_adc_val(energy_estimate)}
    energy_str = make_adc_file_str(expt_id,energy_estimate)
    print("energy ",expt_id," Vsafe is ",energy_vsafe)
    ##----------------------------------------------------------
#Dynamic
    # Re-use energy_vals defined above
    # Start with downsampling
    step = int(np.floor(DYN_SEC_PER_SAMPLE/(energy_vals[1,0] - energy_vals[0,0])))
    # Grab vmin
    Vmin = np.min(energy_vals[::step,1])
    # Grab Vfinal (max) after end
    temp_vals = energy_vals[energy_vals[:,0] > time_by_id[expt_id]]
    Vfinal = np.max(temp_vals[:,0])
    print("Dyn: start,min,final:",start_avg,Vmin,Vfinal)
    dynamic_vsafe =  mmp.calc_vsafe(start_avg,Vmin,Vfinal)
    dynamic_vals[expt_id] = {make_adc_val(dynamic_vsafe)}
    dynamic_str = make_adc_file_str(expt_id,dynamic_vsafe)
    print("dynamic ",expt_id," Vsafe is ",dynamic_vsafe)
#Faster sampling in hardware
    # Re-use energy_vals defined above
    # Start with downsampling
    step = int(np.floor(HW_SEC_PER_SAMPLE/(energy_vals[1,0] - energy_vals[0,0])))
    # Grab vmin
    Vmin = np.min(energy_vals[::step,1])
    # Grab Vfinal (max) after end
    temp_vals = energy_vals[energy_vals[:,0] > time_by_id[expt_id]]
    Vfinal = np.max(temp_vals[:,0])
    print("HW: start,min,final:",start_avg,Vmin,Vfinal)
    hardware_vsafe =  mmp.calc_vsafe(start_avg,Vmin,Vfinal)
    hardware_vals[expt_id] = {make_adc_val(hardware_vsafe)}
    hardware_str = make_adc_file_str(expt_id,hardware_vsafe)
    print("hardware ",expt_id," Vsafe is ",hardware_vsafe)

    if DO_PLOT == True:
      minV.calc_sim_starting_point(I,dt,Vsafe)

    esr_file.write(Vsafe_culpeo_str)
    catnap_file.write(catnap_file_str)
    lucky_file.write(lucky_str)
    unlucky_file.write(unlucky_str)
    energy_file.write(energy_str)
    dynamic_file.write(dynamic_str)
    hardware_file.write(hardware_str)
  esr_file.close()
  catnap_file.close()
  lucky_file.close()
  unlucky_file.close()
  energy_file.close()
  hardware_file.close()

  culpeo_pickle = open('culpeo_vsafe.pkl','wb')
  pickle.dump(culpeo_vals,culpeo_pickle)
  culpeo_pickle.close()
  catnap_pickle = open('catnap_vsafe.pkl','wb')
  pickle.dump(catnap_vals,catnap_pickle)
  catnap_pickle.close()
  energy_pickle = open('energy_vsafe.pkl','wb')
  pickle.dump(energy_vals,energy_pickle)
  energy_pickle.close()
  dynamic_pickle = open('dynamic_vsafe.pkl','wb')
  pickle.dump(dynamic_vals,dynamic_pickle)
  dynamic_pickle.close()
  hardware_pickle = open('hardware_vsafe.pkl','wb')
  pickle.dump(hardware_vals,hardware_pickle)
  hardware_pickle.close()
  lucky_pickle = open('lucky_vsafe.pkl','wb')
  pickle.dump(lucky_vals,lucky_pickle)
  lucky_pickle.close()
  unlucky_pickle = open('unlucky_vsafe.pkl','wb')
  pickle.dump(unlucky_vals,unlucky_pickle)
  unlucky_pickle.close()

