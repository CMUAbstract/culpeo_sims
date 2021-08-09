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
GRP_CNT = 4
VHIGH = 3228
VMIN = 1.6
VMAX = 2.56
VRANGE = 3.1
V_HARD_FAIL = 1.6
bar_width = .2
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

  open_datasheet_vsafe= open('datasheet_vsafe.pkl','rb')
  datasheet_vsafes = pickle.load(open_datasheet_vsafe)
  open_datasheet_vsafe.close()


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

  open_datasheet_summary= open('datasheet_summary.pkl','rb')
  datasheet_expts = pickle.load(open_datasheet_summary)
  open_datasheet_summary.close()

  print("Culpeo_summary")
  print(culpeo_expts)

  labels = []
  culpeo_diffs= []
  catnap_diffs= []
  conservative_diffs= []
  datasheet_diffs= []
  culpeo_vsafes_used= []
  catnap_vsafes_used= []
  conservative_vsafes_used= []
  datasheet_vsafes_used= []
  culpeo_markers = []
  catnap_markers = []
  conservative_markers = []
  datasheet_markers = []
  no_starts = []
  hard_fails = []
  catnap_colors = []
  datasheet_colors = []
  arrs = [catnap_expts,datasheet_expts,conservative_expts,culpeo_expts]
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
      # Handle datasheet
      if (expt_id in datasheet_expts.keys()) == False:
        datasheet_diffs.append(0)
        datasheet_colors.append(red)
      else:
        if (datasheet_expts[expt_id]['avg_min'] < V_HARD_FAIL):
          datasheet_diffs.append(datasheet_expts[expt_id]['avg_min'])
          #datasheet_diffs.append(0)
          print(datasheet_expts[expt_id]['avg_min'])
          datasheet_markers.append('fail')
          datasheet_colors.append(red)
        else:
          #datasheet_diffs.append((datasheet_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
          datasheet_diffs.append(datasheet_expts[expt_id]['avg_min'])
          datasheet_colors.append(blues[2])
          if (list(datasheet_vsafes[expt_id])[0] > VHIGH):
            datasheet_markers.append('no_start')
          else:
            datasheet_markers.append('pass')
      # Handle culpeo
      #culpeo_diffs.append((culpeo_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
      culpeo_diffs.append(culpeo_expts[expt_id]['avg_min'])

      culpeo_vsafes_used.append(list(culpeo_vsafes[expt_id])[0])
      catnap_vsafes_used.append(list(catnap_vsafes[expt_id])[0])
      conservative_vsafes_used.append(list(conservative_vsafes[expt_id])[0])
      datasheet_vsafes_used.append(list(datasheet_vsafes[expt_id])[0])

  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  catnap_xs = Xs - 1.5*bar_width
  bars_catnap = ax.bar(catnap_xs,catnap_diffs, bar_width,label='Catnap', \
  color=catnap_colors, alpha=alphas[3], edgecolor="k")

  datasheet_xs = Xs - .5*bar_width
  bars_datasheet = ax.bar(datasheet_xs,datasheet_diffs,bar_width, label='Datasheet', \
  color=datasheet_colors, alpha=alphas[2],edgecolor="k")

  conservative_xs = Xs + .5*bar_width
  bars_conservative = ax.bar(conservative_xs,conservative_diffs,bar_width, label='Culpeo-PE', \
  color=[blues[2]]*len(Xs), alpha=alphas[1],edgecolor="k")

  culpeo_xs = Xs + 1.5*bar_width
  bars_culpeo = ax.bar(culpeo_xs, culpeo_diffs, bar_width, label='Culpeo',\
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
  datasheet_vsafes = np.divide(np.multiply(datasheet_vsafes_used,VRANGE),4096)
 
  ax.scatter(x=catnap_xs - bar_width/2,y=catnap_vsafes,c=blues[2], alpha = alphas[3],marker="o",edgecolor="k")
  ax.scatter(x=datasheet_xs - bar_width/2,y=datasheet_vsafes,c=blues[2],  alpha = alphas[2],marker="o",edgecolor="k")
  ax.scatter(x=conservative_xs - bar_width/2,y=conservative_vsafes,c=blues[2], alpha = alphas[1],marker="o", edgecolor="k")
  ax.scatter(x=culpeo_xs - bar_width/2,y=culpeo_vsafes,c=blues[2], alpha = alphas[0], marker="o", edgecolor="k")
  ax.set_ylabel('Voltage')
  #plt.ylim(-.1,. 4)
  plt.show()
  fig.savefig('synthetic_loads_plot.pdf',format='pdf',bbox_inches='tight')





