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
    vals = vals[vals[:,0] < 17]
    vals = vals[vals[:,0] > 13]
    fig, ax = plt.subplots()
    ax.plot(vals[:,0],vals[:,1])
    plt.show()
    fig.savefig(name + '_plot.png',format='png',bbox_inches='tight')
    if DO_I:
      fig, ax = plt.subplots()
      diffs = np.subtract(vals[:,3],vals[:,2])
      numbers = re.findall(r'[0-9]+',filename)
      gain = int(numbers[-1])
      print(gain)
      I = np.divide(diffs,R_SHUNT*gain)
      ax.plot(vals[:,0],I)
      ax2 = ax.twinx()
      plt.scatter(vals[:,10],vals[:,11],c='k')
      plt.show()
      fig.savefig(name + '_current_plot.pdf',format='pdf',bbox_inches='tight')

