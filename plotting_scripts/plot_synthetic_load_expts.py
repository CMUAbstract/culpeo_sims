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
bar_width = .2

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

  open_culpeo_summary= open('culpeo_summary.pkl','rb')
  culpeo_expts = pickle.load(open_culpeo_summary)
  open_culpeo_summary.close()
  
  labels = [] 
  culpeo_diffs= []
  catnap_diffs= []
  conservative_diffs= []
  culpeo_vsafes_used= []
  catnap_vsafes_used= []
  conservative_vsafes_used= []
  for expt_id in expts_to_use:
    # check if culpeo's vsafe is above Vhigh, if it is, check if we finished
    # anyway
    if (expt_id in culpeo_expts.keys()) == False:
      continue
    if list(culpeo_vsafes[expt_id])[0] < VHIGH or culpeo_expts[expt_id]['avg_min'] > VMIN:
      culpeo_diffs.append(culpeo_expts[expt_id]['avg_min'] - VMIN)
      catnap_diffs.append(catnap_expts[expt_id]['avg_min'] - VMIN)
      if (expt_id in conservative_expts.keys()) == False:
        conservative_diffs.append(0)
      else:
        conservative_diffs.append(conservative_expts[expt_id]['avg_min'] - VMIN)
      culpeo_vsafes_used.append(list(culpeo_vsafes[expt_id])[0])
      catnap_vsafes_used.append(list(catnap_vsafes[expt_id])[0])
      conservative_vsafes_used.append(list(conservative_vsafes[expt_id])[0])
      labels.append(expt_id)
  Xs = np.arange(len(labels))
  fig, ax = plt.subplots()
  bars_catnap = ax.bar(Xs-bar_width,catnap_diffs,bar_width,label='Catnap')
  bars_conservative = \
  ax.bar(Xs,conservative_diffs,bar_width,label='CBB')
  bars_culpeo = ax.bar(Xs+bar_width,culpeo_diffs,bar_width,label='Culpeo')
  ax.set_ylabel('Diff from Vmin (V)')
  ax.set_xticks(Xs)
  ax.set_xticklabels(labels)
  ax.legend()
  plt.ylim(-.25,.5)
  plt.show()





