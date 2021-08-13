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

#expts_to_use = [3,4,5,6,7,8,9,10,11,12,27,28,29,30,31,32,33,34,35,36]
expts_to_use = [37,38,39]
names = ['Gesture','BLE', 'MNIST']

GRP_CNT = 3
VHIGH = 3228
VMIN = 1.6
VMAX = 2.56
VRANGE = 3.1
V_HARD_FAIL = 1.6
bar_width = .2
LW = 10
CS = 14
MS = 6
FS = 24
alphas=[1,.6,.4,.2]


red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]
colors = ["#f7f7f7","#ca0020","#f4a582","#92c5de","#0571b0"]

if __name__ == "__main__":
  catnap_vsafes = {37:2121,38:2177,39:2530}

  conservative_vsafes = {37:4121,38: 3315, 39:3012}

  culpeo_vsafes = {37: 2909, 38:3038, 39:2871}

  datasheet_vsafes = {37:3220,38: 2289,39:2906}


  open_catnap_summary= open('catnap_37-39_summary.pkl','rb')
  catnap_expts = pickle.load(open_catnap_summary)
  open_catnap_summary.close()

  open_conservative_summary= open('conservative_38-39_summary.pkl','rb')
  conservative_expts = pickle.load(open_conservative_summary)
  open_conservative_summary.close()
  #print("Conservative_summary")
  #print(conservative_expts)

  open_culpeo_summary= open('culpeo_37-39_summary.pkl','rb')
  culpeo_expts = pickle.load(open_culpeo_summary)
  open_culpeo_summary.close()

  open_datasheet_summary= open('datasheet_37-39_summary.pkl','rb')
  datasheet_expts = pickle.load(open_datasheet_summary)
  open_datasheet_summary.close()

  #print("Culpeo_summary")
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
  for expt_count,expt_id in enumerate(expts_to_use):
    # check if culpeo's vsafe is above Vhigh, if it is, check if we finished
    # anyway
    if (expt_id in culpeo_expts.keys()) == False:
      continue
    if culpeo_vsafes[expt_id] < VHIGH or culpeo_expts[expt_id]['avg_min'] > VMIN:
      labels.append(names[expt_count])
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
        if (catnap_vsafes[expt_id] > VHIGH):
          catnap_markers.append('no_start')
        else:
          catnap_markers.append('pass')
      # Handle conservative
      if (expt_id in conservative_expts.keys()) == False:
        conservative_diffs.append(conservative_vsafes[expt_id]*VRANGE/4096)
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
          #print(datasheet_expts[expt_id]['avg_min'])
          datasheet_markers.append('fail')
          datasheet_colors.append(red)
        else:
          #datasheet_diffs.append((datasheet_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
          datasheet_colors.append(blues[2])
          if (datasheet_vsafes[expt_id] > VHIGH):
            datasheet_diffs.append(datasheet_vsafes[expt_id])
            datasheet_markers.append('no_start')
          else:
            datasheet_diffs.append(datasheet_expts[expt_id]['avg_min'])
            datasheet_markers.append('pass')
      # Handle culpeo
      #culpeo_diffs.append((culpeo_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
      culpeo_diffs.append(culpeo_expts[expt_id]['avg_min'])
      if (culpeo_expts[expt_id]['avg_min'] < VMIN):
        print("Fail: ",expt_id)

      culpeo_vsafes_used.append(culpeo_vsafes[expt_id])
      catnap_vsafes_used.append(catnap_vsafes[expt_id])
      conservative_vsafes_used.append(conservative_vsafes[expt_id])
      datasheet_vsafes_used.append(datasheet_vsafes[expt_id])

  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  catnap_xs = Xs - 1.5*bar_width
  catnap_vsafes = np.divide(np.multiply(catnap_vsafes_used,VRANGE),4096)
  catnap_delta = np.subtract(catnap_vsafes,catnap_diffs)
  plt.errorbar(catnap_xs,catnap_vsafes,catnap_delta,fmt='.', markersize=MS,
  linewidth=10,ecolor=colors[1],barsabove=False,\
  marker='_',color = colors[1],mfc=colors[1],elinewidth=LW,uplims=True,capsize=CS,label='Catnap',alpha=1)

  datasheet_xs = Xs - .5*bar_width
  datasheet_vsafes = np.divide(np.multiply(datasheet_vsafes_used,VRANGE),4096)
  datasheet_delta = np.subtract(datasheet_vsafes,datasheet_diffs)
  plt.errorbar(datasheet_xs,datasheet_vsafes,datasheet_delta,fmt='.',elinewidth=LW,
  ecolor=colors[2],\
  marker='_',color=colors[2],mfc=colors[2],uplims=True,capsize=CS,label='Datasheet',alpha=1)

  conservative_xs = Xs + .5*bar_width
  conservative_vsafes = np.divide(np.multiply(conservative_vsafes_used,VRANGE),4096)
  conservative_delta = np.subtract(conservative_vsafes,conservative_diffs)
  plt.errorbar(conservative_xs,conservative_vsafes,conservative_delta,elinewidth=LW,fmt='.',
  ecolor=colors[3],color=colors[3],\
  marker='_',mfc=colors[3],uplims=True,capsize=CS,label='Culpeo-PE',alpha=1)

  culpeo_xs = Xs + 1.5*bar_width
  culpeo_vsafes = np.divide(np.multiply(culpeo_vsafes_used,VRANGE),4096)
  culpeo_delta = np.subtract(culpeo_vsafes,culpeo_diffs)
  plt.errorbar(culpeo_xs,culpeo_vsafes,culpeo_delta,elinewidth=LW,fmt='.', ecolor=colors[4],\
  marker='_',color=colors[4],mfc=colors[4],uplims=True,capsize=CS,label='Culpeo',alpha=1)

  #ax.xaxis.set_label_coords(.75, -.12)
  plt.xticks(Xs,rotation=0,ha='center',fontsize=FS,fontweight=300)
  #ax.annotate('', xy=(.5,-.11), xycoords='axes fraction', xytext=(1, -0.11),
#arrowprops=dict(arrowstyle="-", color='k',lw=1))

  plt.axhline(VMIN,color="black",linestyle='dashed',lw=2)
  plt.axhline(VMAX,color="#91cf60",linestyle='dashed',lw=2)
  for x in Xs:
    plt.axvline(x+2.5*bar_width,color='black',alpha=.5,lw=.5)
  boldness = 300
  ax.annotate("$V_{high}$",(0-1.75*bar_width,VMAX + .01),fontsize=FS,fontweight=boldness)
  ax.annotate("$V_{low}$",(0-1.75*bar_width,VMIN + .01),fontsize=FS,fontweight=boldness)
  ax.set_xticklabels(labels)
  ax.legend(ncol=2,fontsize=FS-2,loc='upper right')
  # Plot vsafe
  #ax2 = ax.twinx()
  #conservative_vsafes = np.divide(np.multiply(conservative_vsafes_used,VRANGE),4096)
  #culpeo_vsafes = np.divide(np.multiply(culpeo_vsafes_used,VRANGE),4096)
  #datasheet_vsafes = np.divide(np.multiply(datasheet_vsafes_used,VRANGE),4096)
 
  #ax.scatter(x=catnap_xs - bar_width/2,y=catnap_vsafes,c=blues[2], alpha = alphas[3],marker="o",edgecolor="k")
  #ax.scatter(x=datasheet_xs - bar_width/2,y=datasheet_vsafes,c=blues[2],  alpha = alphas[2],marker="o",edgecolor="k")
  #ax.scatter(x=conservative_xs - bar_width/2,y=conservative_vsafes,c=blues[2], alpha = alphas[1],marker="o", edgecolor="k")
  #ax.scatter(x=culpeo_xs - bar_width/2,y=culpeo_vsafes,c=blues[2], alpha = alphas[0], marker="o", edgecolor="k")
  ax.set_ylabel('Voltage (V)',fontsize=FS,fontweight=boldness)
  #plt.ylim(-.1,. 4)
  ratio = 1/2
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('mezzos_plot.pdf',format='pdf',bbox_inches='tight')





