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
    bit_flips = vals[:,12:14]
    bit_flips = bit_flips[bit_flips[:,0]<STOP_TIME[count]]
    bit_flips = bit_flips[bit_flips[:,0] > START_TIME[count]]
    bit_flips[:,0] = np.add(bit_flips[:,0],-START_TIME[count])
    vals = vals[vals[:,0] < STOP_TIME[count]]
    vals = vals[vals[:,0] > START_TIME[count]]
    enables = vals[:,6:8]
    enables = enables[enables[:,0]<=STOP_TIME[count]]
    enables = enables[enables[:,0] >= START_TIME[count]]
    times = np.add(vals[:,0],-START_TIME[count])
    if DO_HIST == False:
      axarr[count].grid(True)
      axarr[count].plot(times,vals[:,1])
      axarr[count].set_ylabel('$V^{cap}$ (V)')
      axarr[count].set_title(titles[count])
      axarr[count].set_ylim([1.5,2.7])
      axarr[count].axhline(1.6,c='k',ls='--')
      axarr[count].text(-3,1.63,"$V_{off}$")
      axarr[count].axhline(2.5,c='k',ls='--')
      axarr[count].text(-3,2.35,"$V_{high}$")
      axarr[count].set_xlim(-3,30)
      if count == 2:
        axarr[count].axhline(2.06,c='k',ls='--')
        axarr[count].text(-3,2.1,"$V_{safe}$")

    #axnew = axarr[count].twinx()
    #axnew.scatter(bit_flips[:,0],bit_flips[:,1])
    #TODO this may not work if we start at a value other than 0
    bit_flips = bit_flips[bit_flips[:,1] > 0]
    last_flip = -10
    flip_arrivals = []
    if len(enables[:,0]) < 1:
      enables = np.vstack((enables,[START_TIME[count],1]))
      print(enables)
    if len(enables[:,0]) < 2:
      enables = np.vstack((enables,[STOP_TIME[count] + START_TIME[count],0]))
      print(enables)
    enable_times = np.add(enables[:,0],-START_TIME[count])
    for i,time in enumerate(bit_flips[:,0]):
      if time - last_flip > .002:
        # Walk through enable_times
        for enable_step,enable_time in enumerate(enable_times):
          if time < enable_time:
            print("looking at: ",time,enable_time)
            if enables[enable_step-1,1] == 1:
              flip_arrivals.append(time)
            break;
      last_flip = time
    interarrival = []
    for i, flip in enumerate(flip_arrivals):
      if i == 0:
        continue
      interarrival.append(flip - flip_arrivals[i - 1])
    if DO_HIST == False:
      axarr[count].scatter(flip_arrivals,len(flip_arrivals)*[2.6],lw=1,marker='|',color='#ef8a62')
      axarr[count].annotate("Sense",xy=(1,2.55),xytext=(-3,2.55),color='#ef8a62',
      size='8')#,arrowprops=dict(arrowstyle='->'))#arrowprops=dict(facecolor='#ef8a62', shrink=0.05))
    print(len(flip_arrivals))
    print(flip_arrivals)
    #print(len(interarrival))
    #print(interarrival)
    #print(flip_arrivals)
    print("count is: ", np.nansum(bit_flips[:,1]))
    # Now set up the histograms
    if DO_HIST == True:
      #ns, patches =
      print("Avg is: ",np.median(interarrival))
      axarr[count].hist(interarrival, 50, density=False, facecolor='b', alpha=0.75)
      axarr[count].set_ylabel('Occurrence')
      axarr[count].set_xlim([0,3])
      axarr[count].set_yticks(range(0,10,1))
      plt.grid()
  axarr[len(all_files)-1].set_xlabel('Time (s)')
  fig.savefig('apds_plot.pdf',format='pdf',bbox_inches='tight')
























