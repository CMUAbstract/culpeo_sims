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

expts_to_use = [3,4,5,6,7,8,9,10,11,12,27,28,29,30,31,32,33,34,35,36]
GRP_CNT = 3
VHIGH = 3228
VMIN = 1.6
VMAX = 2.56
V_HARD_FAIL = 1.0
bar_width = .2
VRANGE = 3.17
LW = 1

alphas=[1,.6,.4,.2]

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]

if __name__ == "__main__":
  open_catnap_vsafe= open('catnap_vsafe.pkl','rb')
  catnap_vsafes = pickle.load(open_catnap_vsafe)
  open_catnap_vsafe.close()

  open_conservative_vsafe= open('conservative_vsafe.pkl','rb')
  conservative_vsafes = pickle.load(open_conservative_vsafe)
  open_conservative_vsafe.close()
  open_culpeo_vsafe= open('culpeo_vsafe.pkl','rb')
  culpeo_vsafes = pickle.load(open_culpeo_vsafe)
  open_culpeo_vsafe.close()

  open_catnap_summary= open('catnap_summary.pkl','rb')
  catnap_expts = pickle.load(open_catnap_summary)
  open_catnap_summary.close()

  open_conservative_summary= open('conservative_summary.pkl','rb')
  conservative_expts = pickle.load(open_conservative_summary)
  open_conservative_summary.close()
  print("Conservative_summary")
  print(conservative_expts)

  open_culpeo_summary= open('culpeo_summary.pkl','rb')
  culpeo_expts = pickle.load(open_culpeo_summary)
  open_culpeo_summary.close()
  print("Culpeo_summary")
  print(culpeo_expts)

  
  labels = [] 
  culpeo_diffs= []
  catnap_diffs= []
  conservative_diffs= []
  culpeo_vsafes_used= []
  catnap_vsafes_used= []
  conservative_vsafes_used= []
  culpeo_markers = []
  catnap_markers = []
  conservative_markers = []
  no_starts = []
  hard_fails = []
  catnap_colors = []
  arrs = [catnap_expts,conservative_expts,culpeo_expts]
  for expt_id in expts_to_use:
    # check if culpeo's vsafe is above Vhigh, if it is, check if we finished
    # anyway
    if (expt_id in culpeo_expts.keys()) == False:
      continue
    if list(culpeo_vsafes[expt_id])[0] < VHIGH or culpeo_expts[expt_id]['avg_min'] > VMIN:
      labels.append(expt_id)
      # Handle catnap
      if (catnap_expts[expt_id]['avg_min'] < V_HARD_FAIL):
        catnap_diffs.append(catnap_expts[expt_id]['avg_min'])
        #catnap_diffs.append(0)
        catnap_markers.append('fail')
        catnap_colors.append(red)
      else:
        #catnap_diffs.append((catnap_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
        catnap_diffs.append(catnap_expts[expt_id]['avg_min'])
        catnap_colors.append(blues[2])
        if (list(catnap_vsafes[expt_id])[0] > VHIGH):
          catnap_markers.append('no_start')
        else:
          catnap_markers.append('pass')
      # Handle conservative
      if (expt_id in conservative_expts.keys()) == False:
        conservative_diffs.append(0)
      else:
        #conservative_diffs.append((conservative_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
        conservative_diffs.append(conservative_expts[expt_id]['avg_min'])
      # Handle culpeo
      #culpeo_diffs.append((culpeo_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
      culpeo_diffs.append(culpeo_expts[expt_id]['avg_min'])

      culpeo_vsafes_used.append(list(culpeo_vsafes[expt_id])[0])
      catnap_vsafes_used.append(list(catnap_vsafes[expt_id])[0])
      conservative_vsafes_used.append(list(conservative_vsafes[expt_id])[0])
  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  bars_catnap = ax.bar(Xs-bar_width,catnap_diffs, bar_width,label='Catnap', \
  color=catnap_colors, alpha=alphas[2], edgecolor="k")
  bars_conservative = ax.bar(Xs,conservative_diffs,bar_width, label='Culpeo-PE', \
  color=[blues[2]]*len(Xs), alpha=alphas[1],edgecolor="k")
  bars_culpeo = ax.bar(Xs+bar_width, culpeo_diffs, bar_width, label='Culpeo',\
  color=[blues[2]]*len(Xs), alpha=alphas[0],edgecolor="k")
  ax.set_ylabel('Diff from Vmin (%)')
  ax.set_xticks(Xs)
  plt.axhline(VMIN,color="#b2182b",linestyle='dashed',lw=LW)
  plt.axhline(VMAX,color="#91cf60",linestyle='dashed',lw=LW)
  ax.annotate("$V_{max}$",(-1,VMAX + .0001))
  ax.annotate("$V_{cold-start}$",(-1,VMIN + .0001))
  ax.set_xticklabels(labels)
  ax.legend()
  # Plot vsafe
  #ax2 = ax.twinx()
  catnap_vsafes = np.divide(np.multiply(catnap_vsafes_used,VRANGE),4096)
  conservative_vsafes = np.divide(np.multiply(conservative_vsafes_used,VRANGE),4096)
  culpeo_vsafes = np.divide(np.multiply(culpeo_vsafes_used,VRANGE),4096)
  ax.scatter(x=Xs - bar_width,y=catnap_vsafes,c=blues[0], marker="o",edgecolor="k")
  ax.scatter(x=Xs,y=conservative_vsafes,c=blues[1], marker="o", edgecolor="k")
  ax.scatter(x=Xs+bar_width,y=culpeo_vsafes,c=blues[2], marker="o", edgecolor="k")
  ax.set_ylabel('Voltage')
  #plt.ylim(-.1,. 4)
  plt.show()
  fig.savefig('synthetic_loads_plot.pdf',format='pdf',bbox_inches='tight')





