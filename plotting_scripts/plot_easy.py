import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import pickle
from matplotlib.ticker import AutoMinorLocator


START_TIME = 0
STOP_TIME = 40

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
  vals = vals[vals[:,0] < STOP_TIME]
  vals = vals[vals[:,0] > START_TIME]
  #vals[:,0] = vals[:,0] - START_TIME
  fig, ax = plt.subplots()
  ax.plot(vals[:,0],vals[:,1],lw=3)
  minor_locator = AutoMinorLocator(10)
  ax.xaxis.set_minor_locator(minor_locator)
  plt.grid(which='minor')
  fig.savefig('temp_plot.pdf',format='pdf',bbox_inches='tight')
