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
FS = 20
Y_FS = 20

BRUTE_FORCE_PATH = "../brute_force_vstarts03-20--13-30-06.pkl"
alphas=[1,.6,.4,.2]

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]

labels = ["Too Fast","Achievable","Slow"]

app_labels = ["Periodic Measurement","Activity Reporting"]#,"Noise Monitor/Report"]


#colors = ["#b2182b","#ef8a62","#fddbc7","#f7f7f7","#d1e5f0","#67a9cf","#2166ac"]
colors = ["#b2182b","#67a9cf"]
lines = ["-","--"]

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
}


arrs = []
sys_labels = ["Catnap-PM","Culpeo-PM","Catnap-AR","Culpeo-AR"]
arr_diffs = []
culpeo_sense_vals = []
catnap_sense_vals = []
culpeo_ble_vals = []
catnap_ble_vals = []
if __name__ == "__main__":
  all_files = []
  num_files = len(sys.argv)
  i = 1
  while i < num_files:
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    print(filename)
    is_sense = re.search("sense",filename)
    is_culpeo = re.search("culpeo",filename)
    period = re.search("[0-9]+",filename)
    print("period is:",period)
# Unpickle
    open_vals= open(filename,'rb')
    vals = pickle.load(open_vals)
    open_vals.close()
    if is_culpeo != None:
      if is_sense != None:
        print("culpeo appending: ",100 * (1 - vals['lost']))
        culpeo_sense_vals.append( 100* (1 - vals['lost']))
      else:
        print("culpeo appending: ",100 * (1 - vals['lost']))
        culpeo_ble_vals.append( 100* (1 - vals['lost']))
    else:
      if is_sense != None:
        print("catnap appending: ",100 * (1 - vals['lost']))
        catnap_sense_vals.append( 100* (1 - vals['lost']))
      else:
        print("catnap appending: ",100 * (1 - vals['lost']))
        catnap_ble_vals.append( 100* (1 - vals['lost']))

  arr_diffs = [catnap_sense_vals,culpeo_sense_vals,catnap_ble_vals,culpeo_ble_vals]
  # This chunk should work regardless of the bar chart
  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  #plt.minorticks_on()
  ax.grid(which="both",axis="y")
  for count,arr in enumerate(arr_diffs):
    ax.plot(Xs,arr, label=sys_labels[count], \
    color=colors[int(count % 2)],\
    alpha=1,linestyle=lines[int(np.floor(count/2))],lw=5)
  ax.legend(ncol=1,fontsize=FS,loc="lower right", bbox_to_anchor=[1,.5])
  boldness = 300
  ax.set_xticks(Xs)
  ax.set_xticklabels(labels,fontsize=FS)
  ax.tick_params(axis='x', which='minor', bottom=False)
  ax.set_ylabel('Events captured (%)',fontsize=Y_FS,fontweight=boldness)
  ax.tick_params(axis='y',labelsize=FS)
  ratio = 1/3
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  #ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('missed_events_sensitivity.pdf',format='pdf',bbox_inches='tight')


