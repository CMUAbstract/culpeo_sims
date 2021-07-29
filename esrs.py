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



esrs_by_id = {
1: 34.13,
2: 34.13,
3: 21.59,
4: 21.59,
5: 21.59,
6: 8.689,
7: 8.689,
8: 8.689,
9: 8.689,
10: 3.226,
11: 3.226,
12: 3.226
};

if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  file_str = "vsafe_" + str(V_MIN)
  esr_file = open(file_str,"w")
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    if len(re.findall('fail',filename)) > 0:
      continue
    expt_id = int(re.findall(r'[0-9]+',filename)[0])
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
      plt.show()
    #I = np.add(I,500e-6)
    print("max I is:", max(I))
    dt = vals[1,0] - vals[0,0] 
    Vsafe = minV.calc_min_forward(I,dt,DO_PLOT)
    adc =  np.ceil(4096*Vsafe/V_RANGE)
    adc = int(adc)
    print("Expt ",expt_id," Vsafe is ",Vsafe, " in adc: ",adc)
    adc_str = "#define VSAFE_ID" + str(expt_id) + " " + str(adc) + "\n"
    if DO_PLOT == True:
      minV.calc_sim_starting_point(I,dt,Vsafe)
    esr_file.write(adc_str)
  esr_file.close()

