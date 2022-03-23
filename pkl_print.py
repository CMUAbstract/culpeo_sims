import matplotlib.patches as patches
import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import pickle

vstarts = []
vsafes = []

all_vstarts = {}

if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    fs = open(filename,'rb')
    vals = pickle.load(fs)
    #print(filename,":",vals)
    print(filename)
    print("Vstart",vals['vstart'])
    print("Vsafe",vals['vsafe'])
    vsafes.append(vals['vsafe'])
    vstarts.append(vals['vstart'])
    all_vstarts[vals['expt_id']] = vals['vstart']
    fs.close()
  new_fs = open("brute_force_vstarts.pkl","wb")
  pickle.dump(all_vstarts,new_fs)
  new_fs.close()
  m,b = np.polyfit(vsafes,vstarts,1)
  print("fit: ",m,b)
