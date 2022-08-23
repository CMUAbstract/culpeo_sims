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
STOP_TIME = 500


GAIN = 16
DO_I = False
R_SHUNT = 4.7
DO_HALF = False
DO_POINTS = False
POINTS_IND = 5
SCALE = 1

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
  if DO_POINTS:
    points = vals[:,POINTS_IND:POINTS_IND+2]
  vals = vals[vals[:,0] < STOP_TIME]
  vals = vals[vals[:,0] > START_TIME]
  #vals[:,0] = vals[:,0] - START_TIME
  fig, ax = plt.subplots()
  ax.plot(vals[:,0],SCALE*vals[:,1],lw=3)
  if DO_POINTS:
    points = points[points[:,1] == 1]
    points = points[points[:,0] < STOP_TIME]
    points = points[points[:,0] > START_TIME]
    print("Points first:",points[0,0:2],"Points last:",points[-1,0:2])
    ax.scatter(points[:,0],2*points[:,1])
  minor_locator = AutoMinorLocator(10)
  #ax.xaxis.set_minor_locator(minor_locator)
  plt.grid(which='minor')
  fig.savefig('tempV_plot.pdf',format='pdf',bbox_inches='tight')
  print(vals[:,0])
  plt.show()
  if DO_I:
    fig, ax = plt.subplots()
    if DO_HALF:
      diffs = 2*np.subtract(vals[:,2],2.5)
    else:
      diffs = np.subtract(vals[:,2],vals[:,3])
    print(vals[:,3])
    print(diffs)
    if any(diff < 0 for diff in diffs):
      print("Upside down!")
      diffs = np.subtract(vals[:,2],vals[:,3])
      if DO_HALF:
        diffs = 2*np.subtract(2.5,vals[:,2])
      else:
        diffs = np.subtract(vals[:,3],vals[:,2])
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
    fig.savefig('tempI_plot.pdf',format='pdf',bbox_inches='tight')
    plt.show()
