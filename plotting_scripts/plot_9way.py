import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob

#1. Charge2full:     0.03,  1.25
#4. Catnap at 2.4V:  0.03,  0.095
#4. Culpeo at 2.4V:  0.03,  0.095

#1. Charge2full:     0.03,  1.25
#3. Catnap at 2.1V:  0.41,  0.48 
#3. Culpeo at 2.1V:  38.6,  38.96 

#1. Charge2full:     0.03,  1.25
#2. Catnap at 1.75V: 0.99,  10.275 
#2. Culpeo at 1.75V: 35.165,37.37  

R_SHUNT = 4.7
ADD_EXTRA = [[0,0,0],[1 ,0 ,0], [1 ,0 ,0 ]]
#            2.4,  2.1, 1.7
#STOP_TIME = [[1.25,.095,.095],
#             [1.25 ,.48 ,38.96 ],
#             [1.25 , 10.275 , 37.37]]
#
#START_TIME = [[0.03,0.03,0.03],
#              [.03  ,.41  ,38.6],
#              [.03, .99 ,35.165]]

START_TIME = [[0.03,0.03,0.03],
              [.03  ,.41  ,.99],
              [.03, 38.6 ,35.165]]

STOP_TIME = [[1.25,1.25,1.25],
             [.095 ,.48 ,10.275 ],
             [.095 , 38.96 , 37.37]]


GAIN = 16
titles = ['Charge-to-Full', 'Catnap','Culpeo']
levels = ['Full', 'Culpeo $V_{safe}$','Catnap $V_{safe}$']
DO_HIST = False
if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  fig, ((ctf_24,ctf_21,ctf_16),(cn_24,cn_21,cn_16),(cu_24,cu_21,cu_16)) = plt.subplots(3,3,sharey=True)
  axarr=[[ctf_24,cn_24,cu_24],
         [ctf_21,cn_21,cu_21], 
         [ctf_16,cn_16,cu_16]]
  for count in range(0,3):
    for col, filename in enumerate(all_files):
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
      bit_flips = bit_flips[bit_flips[:,0]<STOP_TIME[col][count]]
      bit_flips = bit_flips[bit_flips[:,0] > START_TIME[col][count]]
      bit_flips[:,0] = np.add(bit_flips[:,0],-START_TIME[col][count])
      vals = vals[vals[:,0] < STOP_TIME[col][count]]
      vals = vals[vals[:,0] > START_TIME[col][count]]
      enables = vals[:,6:8]
      enables = enables[enables[:,0]<=STOP_TIME[col][count]]
      enables = enables[enables[:,0] >= START_TIME[col][count]]
      times = np.add(vals[:,0],-START_TIME[col][count])
      if DO_HIST == False:
        #axarr[count][col].grid(True)
        axarr[count][col].plot(times,vals[:,1])
        axarr[count][col].set_ylabel(titles[col] + ' $V^{cap}$ (V)')
        if col == 0:
          axarr[count][col].set_title(levels[count])
        axarr[count][col].set_ylim([1.5,2.7])
        axarr[count][col].axhline(1.6,c='k',ls='--')
        #axarr[count].text(-3,1.63,"$V_{off}$")
        axarr[count][col].axhline(2.5,c='k',ls='--')
        #axarr[count].text(-3,2.35,"$V_{high}$")
        #axarr[count].set_xlim(-3,30)
        if count == 2:
          axarr[count][col].axhline(2.06,c='k',ls='--')
         # axarr[count].text(-3,2.1,"$V_{safe}$")

      #axnew = axarr[count].twinx()
      #axnew.scatter(bit_flips[:,0],bit_flips[:,1])
      #TODO this may not work if we start at a value other than 0
      bit_flips = bit_flips[bit_flips[:,1] > 0]
      last_flip = -10
      flip_arrivals = []
      if len(enables[:,0]) < 1:
        enables = np.vstack((enables,[START_TIME[col][count],1]))
        print(enables)
      if len(enables[:,0]) < 2:
        enables = np.vstack((enables,[STOP_TIME[col][count] + START_TIME[col][count],0]))
        print(enables)
      enable_times = np.add(enables[:,0],-START_TIME[col][count])
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
        axarr[count][col].scatter(flip_arrivals,len(flip_arrivals)*[2.6],lw=1,marker='|',color='#ef8a62')
        #axarr[count].annotate("Sense",xy=(1,2.55),xytext=(-3,2.55),color='#ef8a62',
        #size='8')#,arrowprops=dict(arrowstyle='->'))#arrowprops=dict(facecolor='#ef8a62', shrink=0.05))
      print(len(flip_arrivals))
      print(flip_arrivals)
      #print(len(interarrival))
      #print(interarrival)
      #print(flip_arrivals)
      print("count is: ", np.nansum(bit_flips[:,1]))
      # Now set up the histograms
    axarr[col][len(all_files)-1].set_xlabel('Time (s)')
  for ax in fig.get_axes():
    ax.label_outer()
  fig.savefig('9way_plot.pdf',format='pdf',bbox_inches='tight')
























