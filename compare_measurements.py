# Kind of defunct now I think...
import min_voltage_notes as minV
import measurement_calcs as meas
import pandas as pd
import numpy as np
import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import re




if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Error: arg format is: [pruned] filename, gain, pruned:True/False, esr")
    sys.exit(0)
  # filename
  filename = sys.argv[1]
  # gain
  minV.gain = int(sys.argv[2])
  if sys.argv[3] == 'True':
    pruned = True
  else:
    pruned = False
  if pruned == False:
    # do prune (hardcode current))
    spacing = 100
    meas.find_min(sys.argv[1],10,spacing)
    start_ind = input("Enter first index")
    end_ind = input("Enter second index")
    start_ind = int(start_ind)*spacing
    end_ind = int(end_ind)*spacing
    cmd = "sed -n \"%s,%sp\" %s | tee %s"%(start_ind,end_ind,filename,filename+"pruned")
    print("Start")
    print(cmd)
    print("End")
    os.system(cmd)
  else:
    minV.CAP_ESR=int(sys.argv[4])
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals = df.values
    diffs = np.subtract(vals[:,3],vals[:,2])
    I = np.divide(diffs,minV.gain*minV.shunt)
    dt = vals[1,0] - vals[0,0] 
    print("Dt is : ",dt)
    new_Vmin = minV.calc_min_forward(I,dt)
    print("Calculated Vsafe = ",new_Vmin)
    minV.calc_sim_starting_point(I,dt,new_Vmin)
    vals2 = np.column_stack((vals[:,0],vals[:,1]))
    minV.calc_sim(I,dt,vals2)



