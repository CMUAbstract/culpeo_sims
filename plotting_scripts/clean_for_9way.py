import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob

START_TIME = 0
STOP_V = 2.503
GAIN = 16
DO_TWIN = 0

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
    for time_tic, volt in enumerate(vals[:,1]):
      #print(volt > 2.5)
      if volt > 2.5:
        print("Inside")
        STOP_TIME = vals[time_tic,0]
        print(STOP_TIME)
        break
    vals = vals[vals[:,0] < STOP_TIME]
    vals = vals[vals[:,0] > START_TIME]
    vals[:,0] = vals[:,0] - START_TIME
    new_df = pd.DataFrame(vals)
    new_df.to_csv('clean_vals.csv',index=False)
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


