import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob

R_SHUNT = 4.7
STOP_TIME = [30,30,45]
START_TIME = [0,0,15]
GAIN = 16
titles = ['Charge-to-Full', 'Catnap','Culpeo']
DO_HIST = True
if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  fig, axarr = plt.subplots(len(all_files), sharex=True)
  for count, filename in enumerate(all_files):
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
    bit_flips = vals[:,12:14]
    bit_flips = bit_flips[bit_flips[:,0]<STOP_TIME[count]]
    bit_flips = bit_flips[bit_flips[:,0] > START_TIME[count]]
    vals = vals[vals[:,0] < STOP_TIME[count]]
    vals = vals[vals[:,0] > START_TIME[count]]
    times = np.add(vals[:,0],-START_TIME[count])
    if DO_HIST == False:
      axarr[count].grid(True)
      axarr[count].plot(times,vals[:,1])
      axarr[count].set_ylabel('$V^{cap}$ (V)')
      axarr[count].set_title(titles[count])
      axarr[count].set_ylim([1.6,2.6])
    #axnew = axarr[count].twinx()
    #axnew.scatter(bit_flips[:,0],bit_flips[:,1])
    bit_flips = bit_flips[bit_flips[:,1] > 0]
    last_flip = -10
    flip_arrivals = []
    for i,time in enumerate(bit_flips[:,0]):
      if time - last_flip > .002:
        flip_arrivals.append(time)
      last_flip = time
    interarrival = []
    for i, flip in enumerate(flip_arrivals):
      if i == 0:
        continue
      interarrival.append(flip - flip_arrivals[i - 1])
    print(len(flip_arrivals))
    print(flip_arrivals)
    #print(len(interarrival))
    #print(interarrival)
    #print(flip_arrivals)
    print("count is: ", np.nansum(bit_flips[:,1]))
    # Now set up the histograms
    if DO_HIST == True:
      #ns, patches =
      axarr[count].hist(interarrival, 50, density=False, facecolor='b', alpha=0.75)
      axarr[count].set_ylabel('Occurrence')
      axarr[count].set_xlim([0,3])
  axarr[len(all_files)-1].set_xlabel('Time (s)')
  fig.savefig('apds_plot.pdf',format='pdf',bbox_inches='tight')























