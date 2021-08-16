import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob

R_SHUNT = 4.7
STOP_TIME = [40,40,40]
START_TIME = [0,0,0]
GAIN = 16
titles = ['Charge-to-Full', 'Catnap','Culpeo']
DO_HIST = False
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
    enables = vals[:,5:7]
    print(enables)
    enables = enables[enables[:,0]<STOP_TIME[count]]
    enables = enables[enables[:,0] > START_TIME[count]]
    bit_flips = vals[:,7:9]
    bit_flips = bit_flips[bit_flips[:,0]<STOP_TIME[count]]
    bit_flips = bit_flips[bit_flips[:,0] > START_TIME[count]]
    bit_flips = bit_flips[bit_flips[:,1] > 0]
    gnd_truth = vals[:,13:15]
    gnd_truth = gnd_truth[gnd_truth[:,0]<STOP_TIME[count]]
    gnd_truth = gnd_truth[gnd_truth[:,0] > START_TIME[count]]
    real_count = 0;
    captured_count = 0;
    up_time = 0
    for i,time in enumerate(enables[:,0]):
      if enables[i,1] == 1:
        # get next one
        if enables[i+1,1] == 1:
          print("Shit")
          sys.exit()
        start = enables[i,0]
        end = enables[i+1,0]
        up_time += end - start
        temp = bit_flips[bit_flips[:,0] < end]
        temp = temp[temp[:,0] > start]
        captured_count += np.nansum(temp[:,1])
    print("Captured is: ",captured_count)
    print("Up time is: ",up_time)
    print("unexpected failures: ",np.nansum(vals[:,4]))
    vals = vals[vals[:,0] < STOP_TIME[count]]
    vals = vals[vals[:,0] > START_TIME[count]]
    times = np.add(vals[:,0],-START_TIME[count])
    if DO_HIST == False:
      axarr[count].grid(True)
      axarr[count].plot(times,vals[:,1])
      ax2 = axarr[count].twinx()
      ax2.plot(enables[:,0],enables[:,1],'r')
      axarr[count].set_ylabel('$V^{cap}$ (V)')
      axarr[count].set_title(titles[count])
      axarr[count].set_ylim([1.6,2.6])
    #axnew = axarr[count].twinx()
    #axnew.scatter(bit_flips[:,0],bit_flips[:,1])
    print("Sum gnd truth: ",np.nansum(gnd_truth[:,1]))
    #print("Sum captured: ",np.nansum(bit_flips[:,1]))
    last_flip = -10
    #flip_arrivals = []
    #for i,time in enumerate(bit_flips[:,0]):
    #  if time - last_flip > .002:
    #    flip_arrivals.append(time)
    #  last_flip = time
    #interarrival = []
    #for i, flip in enumerate(flip_arrivals):
    #  if i == 0:
    #    continue
    #  interarrival.append(flip - flip_arrivals[i - 1])
    #print(len(flip_arrivals))
    #print(flip_arrivals)
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
  fig.savefig('ml_plot.pdf',format='pdf',bbox_inches='tight')
























