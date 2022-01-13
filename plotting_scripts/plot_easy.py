import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import pickle


GAIN = 16
DO_I = True
R_SHUNT = 4.7

if __name__ == "__main__":
  filename = sys.argv[1]
  print(filename)
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  fig, ax = plt.subplots()
  ax.plot(vals[:,0],vals[:,1],lw=3)
  print(vals[:,0])
  plt.show()
  if DO_I:
    fig, ax = plt.subplots()
    diffs = np.subtract(vals[:,3],vals[:,2])
    print(vals[:,3])
    print(diffs)
    if any(diff < 0 for diff in diffs):
      print("Upside down!")
      diffs = np.subtract(vals[:,2],vals[:,3])
    numbers = re.findall(r'[0-9]+',filename)
    if GAIN == 0:
      gain = int(numbers[-1])
    else:
      gain = GAIN
    print(gain)
    print(diffs)
    I = 1000*np.divide(diffs,R_SHUNT*gain)
    print(I)
    ax.plot(vals[:,0],I)
    plt.ylabel("Current (mA)",fontsize=20)
    plt.xlabel("Time (s)",fontsize=20)
    plt.show()
