# Script for extracting the results of the load tests that test how well
# different vsafe calculations match up with reality

import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import re
import glob

configs = {0:1.8, 1:1.6}

file_dict = {}



#while i < num_files:
#  numbers = re.findall(r'[0-9]+',sys.argv[i])
#  expt_id = int(numbers[0])
#  config =int(numbers[1])
#  if expt_id in file_dict{}:
#    file_dict[expt_id].append(sys.argv[i])
#  else:
#    file_dict[expt_id] = []
#    file_dict[expt_id].append(sys.arg[i])
#for expt_id in file_dict:
  
  
Vhigh = 2.47

if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    numbers = re.findall(r'[0-9]+',sys.argv[i])
    expt_id = int(numbers[0])
    config =int(numbers[1])
    if expt_id in file_dict:
      file_dict[expt_id].append(sys.argv[i])
    else:
      file_dict[expt_id] = []
      file_dict[expt_id].append(sys.argv[i])
    i += 1
  total_fails = 0
  for expt_id in file_dict:
    mins = []
    fail_count = 0
    for filename in file_dict[expt_id]:
      numbers = re.findall(r'[0-9]+',filename)
      expt_id = int(numbers[0])
      config =int(numbers[1])
      try:
        df = pd.read_csv(filename, mangle_dupe_cols=True,
             dtype=np.float64, skipinitialspace=True)#skiprows=[0])
      except:
        df = pd.read_csv(filename, mangle_dupe_cols=True,
             dtype=np.float64, skipinitialspace=True,skiprows=[0])
      #print("File name is: ",filename)
      vals = df.values
      start_vcap = np.average(vals[0:100,1])
      #print("Start cap is: ",start_vcap)
      Vmin = np.amin(vals[:,1])
      mins.append(Vmin)
      #print("Vmin is ",Vmin)
      if Vmin < configs[config]:
        fail_count += 1
    print("Expt: ",expt_id," Config: ",config)
    print("\tFailures: ",fail_count,"Average min: ",np.average(mins)," Std dev:",\
    np.std(mins))
    if (start_vcap < 2.42):
      total_fails += fail_count
  print("Total failures is: ",total_fails)



