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

expts_to_use = [3,4,6,7,8,9,27,28,30,31,32,33]
GRP_CNT = 4
VHIGH = 3228
VMIN = 1.6
VMAX = 2.5
VRANGE = 3.3
V_HARD_FAIL = 1.6
bar_width = .25
LW = 1
FS = 24
Y_FS = 28
BAR_DROP = .2
BRUTE_FORCE_PATH = "../brute_force_vstarts03-20--13-30-06.pkl"
alphas=[1,.6,.4,.2]

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]

#labels = ["5mA\n100ms","10mA\n100ms","5mA\n10ms","10mA\n10ms","25mA\n10ms",
#"50mA\n10ms","10mA\n1ms","25mA\n1ms","50mA\n1ms","5mA\n100ms","10mA\n100ms","5mA\n10ms",
#"10mA\n10ms","25mA\n10ms","50mA\n10ms","10mA\n1ms","25mA\n1ms","50mA\n1ms"]
labels = ["5mA\n100ms","10mA\n100ms","5mA\n10ms","10mA\n10ms","25mA\n10ms",
"50mA\n10ms","5mA\n100ms","10mA\n100ms","5mA\n10ms",
"10mA\n10ms","25mA\n10ms","50mA\n10ms"]


colors = ["#b2182b","#ef8a62","#fddbc7","#f7f7f7","#d1e5f0","#67a9cf","#2166ac"]

red = "#b2182b"

blues = ["#deebf7","#9ecae1","#3182bd"]

def f_space(ind,total):
  center = np.floor(total/2)
  return (ind - center)

def convert_back(adc_val):
  return adc_val*VRANGE/4096

label_map = {
"unlucky_vsafe":"Catnap-Slow",
"energy_vsafe":"Energy-Direct",
"lucky_vsafe": "Catnap-Optimistic",
"catnap_vsafe": "Catnap-Measured",
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
        cur_vsafe =convert_back(list(arr[expt])[0])
      except:
        print("Alternate:\t\t",arr[expt])
        cur_vsafe = arr[expt]
      if (cur_vsafe > real_min):
        diffs.append(0)
        oks.append(2)
      else:
        diffs.append(100*(real_min - cur_vsafe)/(VMAX-VMIN))
        oks.append(-10)
    arr_diffs.append(diffs)
    arr_oks.append(oks)

  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  ax.grid(which="both",axis="y")
  for count,arr in enumerate(arr_diffs):
    xs = Xs + f_space(count,len(sys_labels))*bar_width
    print(len(xs),len(arr))
    ax.bar(xs,arr, bar_width,label=sys_labels[count], \
    color=colors[count], alpha=1, edgecolor="k")
    for count2,elem in enumerate(arr_oks[count]):
      if elem > 0:
        ax.annotate(u'\u2713',(xs[count2]-.5*bar_width,1),fontsize=FS+5,fontweight=300,color='g')

  ax.legend(ncol=3,fontsize=FS+2,loc="lower center",bbox_to_anchor=[.5,1])
  ax.set_xlabel('Pulse + 100ms low power compute',fontsize=FS,fontweight=200)
  ax.xaxis.set_label_coords(.75, -BAR_DROP-.05)
  plt.xticks(Xs - bar_width,rotation=0,ha='center',fontsize=FS)
  ax.annotate('', xy=(.5,-BAR_DROP), xycoords='axes fraction', \
  xytext=(1, -BAR_DROP), arrowprops=dict(arrowstyle="-", color='k',lw=1))
  #for x in Xs:
  #  plt.axvline(x+3*bar_width,color='black',alpha=.5,lw=.5)
  boldness = 300
  ax.set_xticklabels(labels,fontsize=FS)
  ax.tick_params(axis='x', which='minor', bottom=False)
  ax.set_ylim(0,80)
  ax.set_ylabel('$V_{safe}$ Error (% Operating Range)',fontsize=Y_FS,fontweight=boldness)
  ax.tick_params(axis='y',labelsize=FS)
  ratio = 1/3
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('vsafes_bg.pdf',format='pdf',bbox_inches='tight')


