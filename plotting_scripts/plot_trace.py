import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob

R_SHUNT = 4.7
DO_I = False
START_TIME = 0
STOP_TIME = 10
GAIN = 16
DO_TWIN = 0

plt.rcParams['font.size'] = '16'

if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    pos = re.search(".csv",filename).start()
    name = filename[:pos]
    print(name)
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals = df.values
    vals = vals[vals[:,0] < STOP_TIME]
    vals = vals[vals[:,0] > START_TIME]
    vals[:,0] = vals[:,0] - START_TIME
    print(max(vals[:,0]))
    fig, ax = plt.subplots()
    ax.set_ylim(1.2,2.5)
    plt.ylabel("$V_{cap}$ (V)",fontsize=20)
    plt.xlabel("Time (s)",fontsize=20)
    ax.plot(vals[:,0],vals[:,1],lw=3)
    ratio = 1/3
    xleft, xright = ax.get_xlim()
    ybottom, ytop = ax.get_ylim()
    ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
    plt.show()
    fig.savefig(name + '_plot.png',format='png',bbox_inches='tight')
    if DO_I:
      fig, ax = plt.subplots()
      diffs = np.subtract(vals[:,3],vals[:,2])
      numbers = re.findall(r'[0-9]+',filename)
      if GAIN == 0:
        gain = int(numbers[-1])
      else:
        gain = GAIN
      print(gain)
      I = 1000*np.divide(diffs,R_SHUNT*gain)
      ax.plot(vals[:,0],I)
      plt.ylabel("Current (mA)",fontsize=20)
      plt.xlabel("Time (s)",fontsize=20)
      if DO_TWIN:
        ax2 = ax.twinx()
        plt.scatter(vals[:,10],vals[:,11],c='k')
      plt.show()
      fig.savefig(name + '_current_plot.pdf',format='pdf',bbox_inches='tight')

