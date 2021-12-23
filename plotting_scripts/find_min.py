import pandas as pd
import sys
import matplotlib
import numpy as np
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob

STOP_TIME =  11
STOP_TIME =  38.96
START_TIME = 38.6

if __name__ == "__main__":
  num_files = len(sys.argv)
  i = 1
  all_files = []
  while i < num_files:
    print(sys.argv[i])
    all_files.append(sys.argv[i])
    i += 1
  for filename in all_files:
    pos = re.search(".csv",filename).start()
    name = filename[:pos]
    print(name)
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])

    vals = df.values
    
    bit_flips = vals[:,12:14]
    bit_flips = bit_flips[bit_flips[:,0]<STOP_TIME]
    bit_flips = bit_flips[bit_flips[:,0] > START_TIME]
    bit_flips[:,0] = np.add(bit_flips[:,0],-START_TIME)
    
    vals = vals[vals[:,0] < STOP_TIME]
    vals = vals[vals[:,0] > START_TIME]
    
    cap_voltages = list(vals[:, 1])


    min_vtg = min(cap_voltages)
    min_idx = cap_voltages.index(min_vtg)
    min_time = vals[min_idx, 0]
    
    max_vtg = max(cap_voltages)
    max_idx = cap_voltages.index(max_vtg)
    max_time = vals[max_idx, 0]
    
    print('[%s] min vtg = %s V at time = %s s' % ( min_idx, min_vtg, min_time ))
    print('[%s] max vtg = %s V at time = %s s' % ( max_idx, max_vtg, max_time ))
    

    closest = min(cap_voltages, key=lambda x:abs(x-2.1))

    print('closest: %s V at %s s' % ( closest, vals[cap_voltages.index(closest), 0]))
  
    print('bitflips: %s' % (bit_flips))

    fig, ax = plt.subplots()
    ax.plot(vals[:,0],vals[:,1],lw=3)
    fig.set_size_inches(20,8)
    fig.savefig('test_plot.png',format='png',bbox_inches='tight')

