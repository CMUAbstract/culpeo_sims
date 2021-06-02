from device_sim import Cap
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

gain = 88
shunt = 4.7
epsilon = 0.001

class VstartMin:
  def __init__(self,V=1.8+epsilon):
    self.Vstart = V
  def update_vstart(self):
    self.Vstart = self.Vstart + epsilon


def calc_min(I,time_step):
  cap = Cap(28e-3,25/4)
  #cap = Cap(21e-3,25/3)
  #cap = Cap(14e-3,25/2)
  #cap = Cap(7e-3,25/1)
  Vmin = 1.8
  done = False
  Vobj = VstartMin()
  Vmax = 2.3
  Vop = 2.5
  while done == False:
    # Reset cap values
    flag = 0
    Vs = []
    cur_time = 0
    times = []
    cap.v_internal = Vobj.Vstart
    cap.V=Vobj.Vstart
    cap.last_i = 0
    print("Start loop ", Vobj.Vstart)
    for i in I:
      new_V = cap.update_v(Vmax,0,Vop,i,1,time_step)
      Vs.append(new_V)
      #print(Vs)
      #print(times)
      times.append(cur_time)
      cur_time = cur_time + time_step
      if (cur_time < 0):
        print("Wtf, why?")
        sys.exit(1)
      if (len(times) != len(Vs)):
        print("Mismatch lengths! ",len(times),len(Vs))
        sys.exit(1)
      if new_V < Vmin:
        Vobj.update_vstart()
        flag = 1
        break;
    if (flag == 0):
      done = True
  print("Vmin actual is: ",Vobj.Vstart)
  fig, ax = plt.subplots()
  print("Scattering ", len(times), len(Vs), len(I))
  ax2 = ax.twinx()
  ax.plot(times,Vs)
  ax2.plot(times,I,'r-')
  plt.show()
  E = 0
  for i in I:
    E = E + i*time_step*Vop
  avg_i = np.average(I)
  max_i = np.amax(I)
  print("Max current is: ", max_i)
  print("Average current is: ", avg_i)
  naive_min = np.sqrt(2*E/cap.cap + Vmin**2) 
  naive_better_min = np.sqrt(2*E/cap.cap + (Vmin + avg_i*cap.r)**2)
  conservative_estimate = np.sqrt(2*E/cap.cap + (Vmin + max_i*cap.r)**2)
  print("Naive estimate: ",naive_min," ",(Vobj.Vstart - naive_min)/(Vmax - Vmin))
  print("ESR with avg: ",naive_better_min," ",(Vobj.Vstart - naive_better_min)/(Vmax - Vmin))
  print("Conservative: ",conservative_estimate," ",(Vobj.Vstart -
  conservative_estimate)/(Vmax - Vmin))


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Error: need file to analyze!")
    sys.exit(0)
  try:
    df = pd.read_csv(sys.argv[1], mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(sys.argv[1], mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  diffs = np.subtract(vals[:,1],vals[:,2])
  I = np.divide(diffs,gain*shunt)
  dt = vals[1,0] - vals[0,0] 
  calc_min(I,dt)
