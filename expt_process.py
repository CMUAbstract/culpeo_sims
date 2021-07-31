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

if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    print("File name is: ",filename)
    vals = df.values
    start_vcap = np.avg(vals[0:100,1])
    print("Start cap is: ",start_vcap)
    Vmin = np.amin(vals[0:1])
    print("Vmin is ",Vmin)


