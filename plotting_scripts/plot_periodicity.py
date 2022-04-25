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

GRP_CNT = 4
VHIGH = 3228
VMIN = 1.6
VMAX = 2.5
VRANGE = 3.3
V_HARD_FAIL = 1.6
bar_width = .3
LW = 1
FS = 30
Y_FS = 30

BRUTE_FORCE_PATH = "../brute_force_vstarts03-20--13-30-06.pkl"
alphas=[1,.6,.4,.2]

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]

labels = ["Periodic\nSensing","Responsive\nReporting",\
"Noise Monitor\nMic","Noise Monitor\nBLE"]


#colors = ["#b2182b","#ef8a62","#fddbc7","#f7f7f7","#d1e5f0","#67a9cf","#2166ac"]
colors = ["#b2182b","#2166ac"]

red = "#b2182b"

blues = ["#deebf7","#9ecae1","#3182bd"]

def f_space(ind,total):
  center = np.floor(total/2)
  return (ind - center)

def convert_back(adc_val):
  return adc_val*VRANGE/4096

label_map = {
"culpeo_sense":"Culpeo",
"catnap_sense": "Catnap",
"culpeo_ble":"Culpeo",
"catnap_ble": "Catnap",
"combo_culpeo":"Culpeo",
"combo_catnap": "Catnap",
}


arrs = []
sys_labels = ["Catnap","Culpeo"]
arr_diffs = []
culpeo_vals = []
culpeo_stds = []
catnap_vals = []
catnap_stds = []
if __name__ == "__main__":
  all_files = []
  num_files = len(sys.argv)
  i = 1
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    print(filename)
    #pos = re.search("_[0-9]",filename).start()
# Get name
    #sys_name = filename[:pos]
    is_culpeo = re.search("culpeo",filename)
# Unpickle
    open_vals= open(filename,'rb')
    vals = pickle.load(open_vals)
    open_vals.close()
    print(vals)
    if is_culpeo != None:
      print("culpeo appending: ",100 * (1 - vals['lost']))
      culpeo_vals.append( 100* (1 - vals['lost']))
      culpeo_stds.append( 100* vals['lost_std'])
    else:
      print("catnap appending: ",100 * (1 - vals['lost']))
      catnap_vals.append( 100 * (1 - vals['lost']))
      catnap_stds.append( 100* vals['lost_std'])

  arr_diffs = [catnap_vals,culpeo_vals]
  arr_stds = [catnap_stds,culpeo_stds]
  # This chunk should work regardless of the bar chart
  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  #plt.minorticks_on()
  ax.grid(which="both",axis="y")
  for count,arr in enumerate(arr_diffs):
    print(arr)
    xs = Xs + f_space(count,len(sys_labels))*bar_width
    ax.bar(xs,arr, bar_width,label=sys_labels[count], \
    color=colors[count], alpha=1, \
    edgecolor="k",yerr=arr_stds[count])
  ax.legend(ncol=2,fontsize=FS,loc="upper center", bbox_to_anchor=[.5,1.25])
  boldness = 300
  ax.set_xticks(Xs)
  ax.set_xticklabels(labels,fontsize=FS)
  ax.tick_params(axis='x', which='minor', bottom=False)
  ax.set_ylabel('Events captured (%)',fontsize=Y_FS,fontweight=boldness)
  ax.tick_params(axis='y',labelsize=FS)
  ratio = 1/4
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('missed_events.pdf',format='pdf',bbox_inches='tight')


