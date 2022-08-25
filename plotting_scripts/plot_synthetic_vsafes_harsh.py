import matplotlib.patches as patches
import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import esr_data
import pickle

expts_to_use = [3,4,6,7,8,9,10,11,12,27,28,30,31,32,33,34,35,36]
GRP_CNT = 4
VHIGH = 3228
VMIN = 1.6
VMAX = 2.5
VRANGE = 3.3
V_HARD_FAIL = 1.6
bar_width = .2
LW = 1
FS = 14
Y_FS = 24
YLIM_LOWER = -10
YLIM_UPPER = 15
BAR_DROP = .15
BRUTE_FORCE_PATH = "../brute_force_vstarts03-20--13-30-06.pkl"
alphas=[1,.6,.4,.2]

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]

labels = ["5mA\n100ms","10mA\n100ms","5mA\n10ms","10mA\n10ms","25mA\n10ms",
"50mA\n10ms","10mA\n1ms","25mA\n1ms","50mA\n1ms","5mA\n100ms","10mA\n100ms","5mA\n10ms",
"10mA\n10ms","25mA\n10ms","50mA\n10ms","10mA\n1ms","25mA\n1ms","50mA\n1ms"]

labels_pop = ["5mA\n100ms","10mA\n100ms","5mA\n10ms","10mA\n10ms","25mA\n10ms",
"50mA\n10ms","10mA\n1ms","25mA\n1ms","50mA\n1ms","5mA\n100ms","10mA\n100ms","5mA\n10ms",
"10mA\n10ms","25mA\n10ms","50mA\n10ms","10mA\n1ms","25mA\n1ms","50mA\n1ms"]

#colors = ["#b2182b","#ef8a62","#fddbc7","#f7f7f7","#d1e5f0","#67a9cf","#2166ac"]
colors = ["#ef8a62","#d1e5f0","#67a9cf","#2166ac"]

red = "#b2182b"

blues = ["#deebf7","#9ecae1","#3182bd"]

def f_space(ind,total):
  center = np.floor(total/2)
  return (ind - center)

def convert_back(adc_val):
  return adc_val*VRANGE/4096

label_map = {"energy_vsafe":"Energy",
"unlucky_vsafe": "Catnap-Realistic",
"lucky_vsafe": "Catnap-Optimistic",
"catnap_vsafe": "Catnap",
"culpeo_vsafe": "Culpeo-PG",
"dynamic_vsafe": "Culpeo-ISR",
"hardware_vsafe": "Culpeo-$\mu$arch"
}


arrs = []
sys_labels = []
arr_diffs = []
arr_oks = []
if __name__ == "__main__":
  all_files = []
  num_files = len(sys.argv)
  i = 1
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    pos = re.search("\.pkl",filename).start()
# Get name
    sys_name = filename[:pos]
    sys_labels.append(label_map[sys_name])
# Unpickle
    open_vsafe= open(filename,'rb')
    vsafes = pickle.load(open_vsafe)
    open_vsafe.close()
    arrs.append(vsafes)
  brute_force_vsafes = pickle.load(open(BRUTE_FORCE_PATH,'rb'))
  for count,arr in enumerate(arrs):
    print(sys_labels[count])
    diffs = []
    oks = []
    for expt in expts_to_use:
      print("\tExpt: ",expt)
      real_min = brute_force_vsafes[expt]
# Accumulate diffs
      print("\t\t",real_min)
      try:
        print("\t\t",convert_back(list(arr[expt])[0]))
        cur_vsafe = ( 100*(convert_back(list(arr[expt])[0]) - real_min)/(VMAX-VMIN))
      except:
        print("Alternate:\t\t",arr[expt])
        cur_vsafe = ( 100*(arr[expt] - real_min)/(VMAX-VMIN))
      diffs.append(cur_vsafe)
      if (cur_vsafe < YLIM_LOWER):
        oks.append(cur_vsafe)
      else:
        oks.append(0)
    arr_diffs.append(diffs)
    arr_oks.append(oks)

  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  #plt.minorticks_on()
  ax.grid(which="both",axis="y", linewidth=2, linestyle='--', alpha=0.35)
  for count,arr in enumerate(arr_diffs):
    print("Count is: ",count)
    print("\t",arr)
    xs = Xs + f_space(count,len(sys_labels))*bar_width
    ax.bar(xs,arr, bar_width,label=sys_labels[count], \
    color=colors[count], alpha=1, edgecolor="k")
    for count2,elem in enumerate(arr_oks[count]):
      if elem < 0:
        ax.annotate(str(int(elem))+"%",(xs[count2]-0.5*bar_width,YLIM_LOWER+1),\
        fontsize=FS+3,fontweight=300,color='k',rotation=90,
		ha='right')
        ax.annotate("~",(xs[count2]-0.8*bar_width,YLIM_LOWER-0.3),
        fontsize=18,fontweight=300,color='k', rotation=90,
		annotation_clip=False)
        ax.annotate("~",(xs[count2]-1*bar_width,YLIM_LOWER-0.3),
        fontsize=18,fontweight=300,color='k', rotation=90,
		annotation_clip=False)

  ax.legend(ncol=4,fontsize=FS+4, loc='center', bbox_to_anchor=[0.5,1.1])
  ax.set_xlabel('Pulse + 100ms low power compute',fontsize=FS,fontweight=200)
  ax.xaxis.set_label_coords(.75, -BAR_DROP-.05)
  plt.xticks(Xs - 0.5*bar_width,rotation=0,ha='center',fontsize=FS)
  ax.annotate('', xy=(.5,-BAR_DROP-0.03), xycoords='axes fraction', \
  xytext=(1, -BAR_DROP-0.03), arrowprops=dict(arrowstyle="-", color='k',lw=1))
  for x in Xs[:-1]:
    plt.axvline(x+2*bar_width,color='black',alpha=.8,lw=1, linestyle=':')
  plt.axhline(0,color='black',alpha=1,lw=1.5, linestyle='-')
  plt.axhline(-2,color='#B20600',alpha=0.8,lw=1.5, linestyle='--')
  plt.fill_between([Xs[0]-6*bar_width,Xs[-1]+6*bar_width],-2,YLIM_LOWER, color='#EE5007', alpha=0.35)
  plt.fill_between([Xs[0]-6*bar_width,Xs[-1]+6*bar_width],-2,YLIM_UPPER, color='#E4E9BE', alpha=0.8)
  
  ax.arrow(Xs[0]-4*bar_width,-2,0,YLIM_UPPER+2, 
  color='#224B0C', width=0.05, head_length=1,length_includes_head=True)
  ax.annotate("SAFE", (Xs[0]-3*bar_width, (YLIM_UPPER-2)),
   fontsize=FS+5, fontweight=300, ha='left', va='center', 
   annotation_clip=False, rotation=0, color='#224B0C')

  ax.arrow(Xs[0]-4*bar_width,-2,0,YLIM_LOWER+2, 
  color='#B20600', width=0.05, head_length=1,length_includes_head=True)
  ax.annotate("UNSAFE", (Xs[0]-3*bar_width, (YLIM_LOWER+2)),
   fontsize=FS+5, fontweight=300, ha='left', va='center', 
   annotation_clip=False, rotation=0, color='#B20600')
  ax.annotate("\N{MINUS SIGN}2", (Xs[0]-1.35, -2),
   fontsize=FS, fontweight=300, ha='right', va='center', 
   annotation_clip=False, rotation=0, color='#B20600')
  
  
  boldness = 300
  note_pos = (-1,YLIM_LOWER+2)
  arrow_pos = (1+bar_width*2,7.5)
  #ax.annotate("Must be > -2% for correctness\nLower is better for performance", \
  #note_pos, fontsize=FS+4,fontweight=boldness,zorder=10, annotation_clip=False)
  #ax.arrow(note_pos[0]+.1,note_pos[1],arrow_pos[0]-note_pos[0],arrow_pos[1]-note_pos[1])

  ax.set_xticklabels(labels,fontsize=FS)
  ax.tick_params(axis='x', which='minor', bottom=False)
  ax.set_xlim(Xs[0]-6*bar_width,Xs[-1]+3*bar_width)
  ax.set_ylim(YLIM_LOWER,YLIM_UPPER)
  ax.set_ylabel('$V_{safe}$ Error (%)',fontsize=Y_FS-2,fontweight=boldness)
  ax.tick_params(axis='y',labelsize=FS)
  ratio = 1/4
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('synthetic_loads_vsafe.pdf',format='pdf',bbox_inches='tight')


