import matplotlib.patches as mpatches
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
bar_width = .1
LW = 1
FS = 30
Y_FS = 34
spacer = 1*bar_width
LINE_DROP = .1
LINE_SPACE = .07
def f_space(ind,total):
  center = np.floor(total/2)
  return (ind - center)

BRUTE_FORCE_PATH = "../brute_force_vstarts03-20--13-30-06.pkl"
alphas=[1,.6,.4,.2]

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]

labels = ["Slow","Achievable","Too Fast"]

app_labels = ["Periodic Sensing","Responsive Reporting"]#,"Noise Monitor/Report"]

systems = ["Culpeo","Catnap"]
#colors = ["#b2182b","#ef8a62","#fddbc7","#f7f7f7","#d1e5f0","#67a9cf","#2166ac"]
#colors = ["#b2182b","#67a9cf"]
#colors = ["#b2182b","#f7f7f7","#67a9cf"]
colors = [["#b2182b","#ef8a62","#fddbc7"],["#2166ac","#67a9cf","#d1e5f0"]]
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
sys_labels = ["Catnap","Culpeo"]
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

  arr_diffs = [[catnap_sense_vals,culpeo_sense_vals],\
  [catnap_ble_vals,culpeo_ble_vals]]
  # This chunk should work regardless of the bar chart
  Xs = np.arange(3)
  print(Xs)
  fig, ax = plt.subplots()
  #plt.minorticks_on()
  ax.grid(which="both",axis="y")
  for count,arr in enumerate(arr_diffs):#app
    print("Count0",count)
    for count2,arr2 in enumerate(arr):#system
      print("Count2",count2)
      xs = count + Xs*bar_width \
      + count2*bar_width*len(labels)+count2*spacer # for 2nd grp
      print(xs,arr2)
      vals_plot = [arr2[2],arr2[1],arr2[0]]
      if (count == 0):
        cur_label = sys_labels[count2]
      else:
        cur_label = None
      print(vals_plot)
      ax.bar(xs,vals_plot,bar_width ,label=labels, \
      color=colors[count2],\
      alpha=1,edgecolor="k")
  #ax.legend(ncol=1,fontsize=FS,loc="lower right", bbox_to_anchor=[1,.5])
  boldness = 300
  ax.set_xticks([.125,.5,1.125,1.5])
  full_labels = ['Catnap','Culpeo','Catnap','Culpeo']
  ax.set_xticklabels(full_labels,fontsize=FS)
  ax.annotate('', xy=(.55,-LINE_DROP), xycoords='axes fraction', xytext=(1, -LINE_DROP),
arrowprops=dict(arrowstyle="-", color='k',lw=1))
  ax.annotate('', xy=(0,-LINE_DROP), xycoords='axes fraction', xytext=(.45, -LINE_DROP),
arrowprops=dict(arrowstyle="-", color='k',lw=1))
  note_pos1 = (.125,-LINE_DROP-LINE_SPACE)
  note_pos2 = (.6,-LINE_DROP-LINE_SPACE)
  label0 = ax.annotate(app_labels[0],xy=note_pos1, \
  xycoords='axes fraction', annotation_clip=False,\
  fontsize=FS+4,fontweight=boldness)
  #ax.text(.15,-.05,"Periodic Measurement", \
  #fontsize=FS+4,fontweight=boldness)
  label1 =ax.annotate(app_labels[1], xy=note_pos2,\
  xycoords='axes fraction', annotation_clip=False,\
  fontsize=FS+4,fontweight=boldness)
  #ax.text(1.15,-.05,"Responsive Sensing",\
  #fontsize=FS+4,fontweight=boldness)
  ax.tick_params(axis='x', which='minor', bottom=False)
  ax.set_ylabel('Events captured (%)',fontsize=Y_FS,fontweight=boldness)
  ax.tick_params(axis='y',labelsize=FS)

  lgd = []
  legs=[]
  ratio = 1/3
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.tight_layout()
  for count,speed in enumerate(labels):
    legs.append(mpatches.Patch(fc=colors[0][count],lw=6,alpha=1,ec=colors[1][count],label=speed))
  lgd =fig.legend(handles=legs,loc='center',bbox_to_anchor=[.6,.65],\
  ncol=1,fontsize=FS)
  plt.show()
  fig.savefig('missed_events_sensitivity.pdf',format='pdf',bbox_inches='tight',bbox_extra_artists=(lgd,label0,label1))


