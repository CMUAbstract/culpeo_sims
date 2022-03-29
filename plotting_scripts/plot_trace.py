import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import pickle

R_SHUNT = 4.7
DO_I = True
START_TIME = .99
STOP_TIME = 1.100
GAIN = 16
DO_TWIN = 0
DO_PLOTS = True

def convert(adc_val):
  return adc_val*2.485/4096


plt.rcParams['font.size'] = '16'

if __name__ == "__main__":
  open_culpeo_vsafe= open('culpeo_vsafe.pkl','rb')
  culpeo_vsafes = pickle.load(open_culpeo_vsafe)
  open_culpeo_vsafe.close()
  open_conservative_vsafe= open('conservative_vsafe.pkl','rb')
  conservative_vsafes = pickle.load(open_conservative_vsafe)
  open_conservative_vsafe.close()
  open_datasheet_vsafe= open('datasheet_vsafe.pkl','rb')
  datasheet_vsafes = pickle.load(open_datasheet_vsafe)
  open_datasheet_vsafe.close()
  open_catnap_vsafe= open('catnap_vsafe.pkl','rb')
  catnap_vsafes = pickle.load(open_catnap_vsafe)
  open_catnap_vsafe.close()
  vsafes = { "catnap":catnap_vsafes, "conservative":conservative_vsafes,
  "culpeo":culpeo_vsafes, "datasheet":datasheet_vsafes}
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    pos = re.search(".csv",filename).start()
    pos2 = re.search("EXPT",filename,re.IGNORECASE).end()
    name = filename[:pos]
    name = name[pos2:]
    numbers = re.findall(r'[0-9]+',name)
    expt_id = int(numbers[0])
    print(expt_id)
    if expt_id < 13:
      START_TIME = 0.99
      STOP_TIME = 1.100
    elif expt_id < 37:
      START_TIME = 0.0
      STOP_TIME = 0.3
    else:
      START_TIME = 0
      STOP_TIME = 10
    # Strip vsafe system
    pos2 = re.search("Vsafe",name).end()
    stripped = name[pos2:]
    system = re.findall(r'[a-z]+',stripped)
    print(stripped)
    cur_vsafes = vsafes[system[0]]
    #print(name)
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals = df.values
    vals = vals[vals[:,0] < STOP_TIME]
    vals = vals[vals[:,0] > START_TIME]
    vals[:,0] = vals[:,0] - START_TIME
    #print(max(vals[:,0]))
    try:
      vsafe = convert(list(cur_vsafes[expt_id])[0])
    except:
      vsafe = 3.3
    vstart = np.average(vals[0:100,1])
    vdiff = vstart - vsafe
    vdiff = vdiff/(2.5-1.6)
    #if (abs(vdiff) > 0.02 and vsafe < 2.42):
    if abs(vdiff) > 0.04:
      print(expt_id," Vsafe vstart diff ", vdiff, "Vsafe:",vsafe,
      "Vstart:",vstart,"Vcap min:", min(vals[:,1]))
    #else:
    #  print(filename)
    if DO_PLOTS == False:
      continue
    fig, ax = plt.subplots()
    ax.set_ylim(1.2,2.5)
    plt.ylabel("$V_{cap}$ (V)",fontsize=20)
    plt.xlabel("Time (s)",fontsize=20)
    ax.plot(vals[:,0],vals[:,1],lw=3)
    ratio = 1/3
    xleft, xright = ax.get_xlim()
    ybottom, ytop = ax.get_ylim()
    ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
    plt.show()
    fig.savefig(name + '_plot.pdf',format='pdf',bbox_inches='tight')
    if DO_I:
      fig, ax = plt.subplots()
      diffs = np.subtract(vals[:,3],vals[:,2])
      if any(diff < 0 for diff in diffs):
        print("Upside down!")
        diffs = np.subtract(vals[:,2],vals[:,3])
      numbers = re.findall(r'[0-9]+',filename)
      if GAIN == 0:
        gain = int(numbers[-1])
      else:
        gain = GAIN
      print(gain)
      I = 1000*np.divide(diffs,R_SHUNT*gain)
      ax.plot(vals[:,0],I)
      plt.ylabel("Current (mA)",fontsize=20)
      plt.xlabel("Time (s)",fontsize=20)
      if DO_TWIN:
        ax2 = ax.twinx()
        plt.scatter(vals[:,10],vals[:,11],c='k')
      #plt.show()
      fig.savefig(name + '_current_plot.pdf',format='pdf',bbox_inches='tight')

