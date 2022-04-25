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
#VHIGH = 3228
VMIN = 1.6
VMAX = 2.5
VHIGH = VMAX
VRANGE = 3.3
V_HARD_FAIL = 1.6
bar_width = .2
LW = 10
CS = 14 # Maps to 0.1V so don't change this!!!
CS_diff = 0.1
MS = 6
FS = 34
alphas=[1,.6,.4,.2]

def convert(adc):
  return adc*VRANGE/4096 

red = "#b2182b"
blues = ["#deebf7","#9ecae1","#3182bd"]
colors = ["#f7f7f7","#ca0020","#f4a582","#92c5de","#0571b0"]

if __name__ == "__main__":
  open_catnap_summary= open('catnap_37-39.pkl','rb')
  catnap_expts = pickle.load(open_catnap_summary)
  open_catnap_summary.close()

  open_energy_summary= open('energy_37-39.pkl','rb')
  energy_expts = pickle.load(open_energy_summary)
  open_energy_summary.close()
  #print("Conservative_summary")
  #print(conservative_expts)

  open_culpeo_summary= open('culpeo_37-39.pkl','rb')
  culpeo_expts = pickle.load(open_culpeo_summary)
  open_culpeo_summary.close()

  open_dynamic_summary= open('dynamic_37-39.pkl','rb')
  dynamic_expts = pickle.load(open_dynamic_summary)
  open_dynamic_summary.close()

  #print("Culpeo_summary")
  print(culpeo_expts)

  labels = []
  culpeo_diffs= []
  catnap_diffs= []
  energy_diffs= []
  dynamic_diffs= []
  culpeo_vsafes_used= []
  catnap_vsafes_used= []
  energy_vsafes_used= []
  dynamic_vsafes_used= []
  no_starts = []
  hard_fails = []
  catnap_colors = []
  dynamic_colors = []
  arrs = [energy_expts,catnap_expts,culpeo_expts,dynamic_expts]
  print("Culpeo outputs:")
  print(culpeo_expts)
  for expt_count,expt_id in enumerate(expts_to_use):
    # check if culpeo's vsafe is above Vhigh, if it is, check if we finished
    # anyway
    if (expt_id in culpeo_expts.keys()) == False:
      continue
    if culpeo_expts[expt_id]['avg_min'] > VMIN:
      labels.append(names[expt_count])
      # Handle catnap
      if (catnap_expts[expt_id]['avg_min'] < V_HARD_FAIL):
        catnap_diffs.append(catnap_expts[expt_id]['avg_min'])
        #catnap_diffs.append(0)
        catnap_colors.append(red)
      else:
        #catnap_diffs.append((catnap_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
        catnap_diffs.append(catnap_expts[expt_id]['avg_min'])
        catnap_colors.append(blues[2])
      # Handle conservative
      if (expt_id in energy_expts.keys()) == False:
        energy_diffs.append(0)
      else:
        #energy_diffs.append((energy_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
        energy_diffs.append(energy_expts[expt_id]['avg_min'])
      # Handle datasheet
      if (expt_id in dynamic_expts.keys()) == False:
        dynamic_diffs.append(0)
        dynamic_colors.append(red)
      else:
        if (dynamic_expts[expt_id]['avg_min'] < V_HARD_FAIL):
          dynamic_diffs.append(dynamic_expts[expt_id]['avg_min'])
          #dynamic_diffs.append(0)
          #print(dynamic_expts[expt_id]['avg_min'])
          dynamic_colors.append(red)
        else:
          #dynamic_diffs.append((dynamic_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
          dynamic_colors.append(blues[2])
          if (dynamic_expts[expt_id]['avg_start'] > VHIGH):
            dynamic_diffs.append(dynamic_vsafes[expt_id])
          else:
            dynamic_diffs.append(dynamic_expts[expt_id]['avg_min'])
      # Handle culpeo
      #culpeo_diffs.append((culpeo_expts[expt_id]['avg_min'] - VMIN)/(VMAX-VMIN))
      culpeo_diffs.append(culpeo_expts[expt_id]['avg_min'])
      print(culpeo_diffs)
      if (culpeo_expts[expt_id]['avg_min'] < VMIN):
        print("Fail: ",expt_id)

      culpeo_vsafes_used.append(culpeo_expts[expt_id]['avg_start'])
      catnap_vsafes_used.append(catnap_expts[expt_id]['avg_start'])
      energy_vsafes_used.append(energy_expts[expt_id]['avg_start'])
      dynamic_vsafes_used.append(dynamic_expts[expt_id]['avg_start'])

  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  energy_xs = Xs - 1.5*bar_width
  #energy_vsafes = np.divide(np.multiply(energy_vsafes_used,VRANGE),4096)
  energy_vsafes = energy_vsafes_used
  energy_delta = np.subtract(energy_vsafes,energy_diffs) - CS_diff
  plt.errorbar(energy_xs,energy_vsafes,energy_delta,elinewidth=LW,fmt='.',
  ecolor=colors[1],color=colors[1],\
  marker='_',mfc=colors[1],uplims=True,capsize=CS,label='Energy-Direct',alpha=1)

  catnap_xs = Xs - .5*bar_width
  #catnap_vsafes = np.divide(np.multiply(catnap_vsafes_used,VRANGE),4096)
  catnap_vsafes = catnap_vsafes_used
  catnap_delta = np.subtract(catnap_vsafes,catnap_diffs) - CS_diff
  plt.errorbar(catnap_xs,catnap_vsafes,catnap_delta,fmt='.', markersize=MS,
  linewidth=10,ecolor=colors[2],barsabove=False,\
  marker='_',color = colors[2],mfc=colors[2],elinewidth=LW,uplims=True,capsize=CS,label='Catnap',alpha=1)


  culpeo_xs = Xs + .5*bar_width
  #culpeo_vsafes = np.divide(np.multiply(culpeo_vsafes_used,VRANGE),4096)
  culpeo_vsafes = culpeo_vsafes_used
  culpeo_delta = np.subtract(culpeo_vsafes,culpeo_diffs) - CS_diff
  plt.errorbar(culpeo_xs,culpeo_vsafes,culpeo_delta,elinewidth=LW,fmt='.', ecolor=colors[3],\
  marker='_',color=colors[3],mfc=colors[3],uplims=True,capsize=CS,label='Culpeo-PG',alpha=1)

  dynamic_xs = Xs + 1.5*bar_width
  #dynamic_vsafes = np.divide(np.multiply(dynamic_vsafes_used,VRANGE),4096)
  dynamic_vsafes = dynamic_vsafes_used
  dynamic_delta = np.subtract(dynamic_vsafes,dynamic_diffs) - CS_diff
  plt.errorbar(dynamic_xs,dynamic_vsafes,dynamic_delta,fmt='.',elinewidth=LW,
  ecolor=colors[4],\
  marker='_',color=colors[4],mfc=colors[4],uplims=True,capsize=CS,label='Culpeo-R',alpha=1)

  #ax.xaxis.set_label_coords(.75, -.12)
  plt.xticks(Xs,rotation=0,ha='center',fontsize=FS,fontweight=300)
  #ax.annotate('', xy=(.5,-.11), xycoords='axes fraction', xytext=(1, -0.11),
#arrowprops=dict(arrowstyle="-", color='k',lw=1))

  plt.axhline(VMIN,color="black",linestyle='dashed',lw=5)
  plt.axhline(VMAX,color="#91cf60",linestyle='dashed',lw=5)
  for x in Xs:
    plt.axvline(x+2.5*bar_width,color='black',alpha=.5,lw=.5)
  boldness = 300
  vsafe_pos = (0-1.75*bar_width,VMAX - .1)
  ax.annotate("$V_{safe}$", vsafe_pos, \
  fontsize=FS,fontweight=boldness)
  ax.arrow(vsafe_pos[0],vsafe_pos[1],.5*bar_width-vsafe_pos[0],2.15-vsafe_pos[1])

  vmin_pos = (0-1.75*bar_width,VMIN + .4)
  ax.annotate("$V_{min}$", vmin_pos, \
  fontsize=FS,fontweight=boldness)
  ax.arrow(vmin_pos[0],vmin_pos[1],.5*bar_width-vmin_pos[0],1.9-vmin_pos[1])

  ax.annotate("$V_{high}$",(2+1.75*bar_width,VMAX + .02),fontsize=FS,fontweight=boldness)
  ax.annotate("$V_{off}$",(2+1.75*bar_width,VMIN + .02),fontsize=FS,fontweight=boldness)
  ax.set_xticklabels(labels,fontsize=FS)
  ax.legend(ncol=1,fontsize=FS-4,loc='lower right',\
  bbox_to_anchor=[1.02,0])#,bbox_to_anchor=[0.4, 0])
  ax.tick_params(labelsize=FS)
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
  plt.minorticks_on()
  ax.grid(which="both",axis="y")
  #plt.ylim(-.1,. 4)
  ratio = 1/2
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('mezzos_plot.pdf',format='pdf',bbox_inches='tight')





