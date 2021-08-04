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


DO_PLOT = False
V_RANGE = 3.17
V_MIN = 1.6
CAP_VAL = 45e-3
EFF_VMIN = .5
#CAP_VAL = 63e-3

esrs = {
1000: 34.13,
100: 21.59,
10: 8.689,
1: 3.226
}

#1 5mA for 1s
#2 10mA for 1s
#3 5mA for 100ms
#4 10mA for 100ms
#5 25mA for 100ms
#6 5mA for 10ms
#7 10mA for 10ms
#8 25mA for 10ms
#9 50mA for 10ms
#10 10mA for 1ms
#11 25mA for 1ms
#12 50mA for 1ms


#esrs_by_id = {
#1: 34.13,
#2: 34.13,
#3: 21.59,
#4: 21.59,
#5: 21.59,
#6: 8.689,
#7: 8.689,
#8: 8.689,
#9: 8.689,
#10: 3.226,
#11: 3.226,
#12: 3.226,
#13: 34.13,
#14: 34.13,
#15: 21.59,
#16: 21.59,
#17: 21.59,
#18: 8.689,
#19: 8.689,
#20: 8.689,
#21: 8.689,
#22: 3.226,
#23: 3.226,
#24: 3.226,
#25: 34.13,
#26: 34.13,
#27: 21.59,
#28: 21.59,
#29: 21.59,
#30: 8.689,
#31: 8.689,
#32: 8.689,
#33: 8.689,
#34: 3.226,
#35: 3.226,
#36: 3.226,
#};

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

def make_adc_file_str(expt_id, val):
  adc = np.ceil(4096*val/V_RANGE)
  adc_val = int(adc)
  file_str = "#define VSAFE_ID" + str(expt_id) + " " + str(adc_val) + "\n"
  return file_str


if __name__ == "__main__":
  file_str = "vsafe_" + str(V_MIN) + "_" + str(CAP_VAL)
  esr_file = open(file_str,"w")

  file_str = "catnap_" + str(V_MIN) + "_" + str(CAP_VAL)
  catnap_file = open(file_str,"w")

  file_str = "naive_" + str(V_MIN) + "_" + str(CAP_VAL)
  naive_file = open(file_str,"w")

  file_str = "naive_better_" + str(V_MIN) + "_" + str(CAP_VAL)
  naive_better_file = open(file_str,"w")

  file_str = "grey_hat_culpeo_" + str(V_MIN) + "_" + str(CAP_VAL)
  conservative_file = open(file_str,"w")

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
    if (expt_id < 13):
      vals = vals[vals[:,0]>1]
      vals = vals[vals[:,0]<2.5]
    diffs = np.subtract(vals[:,3],vals[:,2])
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
    # Catnap
    catnap_E = .5*CAP_VAL*(start_avg**2 - stop_avg**2)
    catnap_Vsafe = np.sqrt(2*catnap_E/CAP_VAL + V_MIN**2)
    catnap_file_str = make_adc_file_str(expt_id,catnap_Vsafe)
    ##----------------------------------------------------------
    # Estimate E with some understanding of the power system
    E = 0
    n = EFF_VMIN
    for i in I:
      E = E + i*dt*2.56/n
    avg_i = np.average(I)/n
    Vcaps = vals[:,1]
    Vcap_min = min(vals[:,1])
    Vcap_min_index = np.argmin(Vcaps)
    print("Min at index ",Vcap_min_index," out of ",len(Vcaps))
    print("Min is",Vcap_min)
    max_i = np.amax(I)*2.56/(n*V_MIN)


    naive_min = np.sqrt(2*E/CAP_VAL + V_MIN**2)
    naive_min_str = make_adc_file_str(expt_id,naive_min)

    naive_better_min = np.sqrt(2*E/CAP_VAL + (V_MIN + avg_i*minV.CAP_ESR)**2)
    naive_better_min_str = make_adc_file_str(expt_id,naive_better_min)

    # Use E from Catnap!!
    # Use Vmin of the system
    conservative_estimate = np.sqrt(2*catnap_E/CAP_VAL + (V_MIN + max_i*minV.CAP_ESR)**2)
    print("Conservative2: ",conservative_estimate)
    conservative_str = make_adc_file_str(expt_id,conservative_estimate)

    Vsafe = minV.calc_min_forward(I,dt,DO_PLOT)
    Vsafe_culpeo_str = make_adc_file_str(expt_id,Vsafe)
    print("Expt ",expt_id," Vsafe is ",Vsafe)
    if DO_PLOT == True:
      minV.calc_sim_starting_point(I,dt,Vsafe)

    esr_file.write(Vsafe_culpeo_str)
    catnap_file.write(catnap_file_str)
    naive_file.write(naive_min_str)
    naive_better_file.write(naive_better_min_str)
    conservative_file.write(conservative_str)
  esr_file.close()
  catnap_file.close()
  naive_file.close()
  naive_better_file.close()
  conservative_file.close()

