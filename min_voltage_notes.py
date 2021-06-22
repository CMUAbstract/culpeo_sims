from device_sim import Cap
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

gain = 88
shunt = 4.7
epsilon = 0.001

# Power save disabled, TPS 61200
# For VOut = 5V
#3.6 : {.0002:.02, .0003:.03,.0005:.05, .001:.10, .002: .20, .004:.30, .006:.40,
#.008:.50, .015:.60, .02:.7, .04:.8,.1:.9,.2:93,.5:.92},

# For VOut = 3.3V
efficiency_table = {2.4 : { .0001: .02, .0002:.04, .0003:.05,.0005:.07, .001:.15, .002: .25, .004:.40,
.006:.50,.008:.60, .015:.70, .02:.75, .03:.8,.1:.9,.2:92,.6:.80},
1.8 : { .0001: .02, .0002:.04, .0003:.05,.0005:.07, .001:.13, .002: .22, .004:.37,
.006:.47,.008:.57, .015:.70, .02:.72, .03:.8,.1:.87,.2:85,.4:.80},
.9: { .0001: .02, .0002:.04, .0003:.05,.0005:.07, .001:.15, .002: .25, .004:.40,
.006:.50,.008:.60, .015:.70, .02:.72, .03:.77,.1:.75,.15:.70,.2:.6}
}

efficiency_table_ps = {2.4 : { .0001: .45, .0002:.60, .0003:.65,.0005:.70,
.001:.75, .002: .78, .004:.79, .006:.79,.008:.80, .015:.80, .02:.81,
.03:.82,.1:.84,.2:.85,.6:.85},
1.8 : { .0001: .45, .0002:.55, .0003:.6,.0005:.65, .001:.70, .002: .72, .004:.74,
.006:.75,.008:.76, .015:.76, .02:.76, .03:.76,.1:.77,.2:.83,.4:.81},
.9: { .0001: .35, .0002:.42, .0003:.46,.0005:.5, .001:.52, .002: .53, .004:.54,
.006:.55,.008:.57, .015:.57, .02:.58, .03:.6,.1:.75,.15:.70,.2:.6}
}
def find_nearest(array,value):
  new_array = np.asarray(array)
  new_arr = new_array - value
  new_new_arr = np.absolute(new_arr)
  idx = new_new_arr.argmin()
  return array[idx]

def get_eff(V_in,I_out,eff):
  V = find_nearest([*eff.keys()],V_in)
  I = find_nearest([*eff[V].keys()],I_out)
  return eff[V][I]


class VstartMin:
  def __init__(self,V=1.8+epsilon):
    self.Vstart = V
  def update_vstart(self):
    self.Vstart = self.Vstart + epsilon

def calc_sim_starting_point(I, time_step,Vstart):
  cap = Cap(15e-3,25/2)
  #cap = Cap(7e-3,25/1)
  Vmin = 1.81
  Vmax = 2.3
  Vop = 2.56
  # Reset cap values
  flag = 0
  Vs = []
  cur_time = 0
  times = []
  cap.v_internal = Vstart
  cap.V=Vstart
  cap.last_i = 0
  Vs.append(cap.V)
  times.append(cur_time)
  for i in I:
    cur_time = cur_time + time_step
    new_V = cap.update_v(Vmax,0,Vop,i,get_eff(cap.V,i,efficiency_table_ps),time_step)
    if (new_V < Vmin):
      print("Error! value too low: ",new_V,i,cur_time)
    #new_V = cap.update_v(Vmax,0,Vop,i,1,time_step)
    #print("New V is: ",new_V)
    Vs.append(new_V)
    #print(Vs)
    #print(times)
    times.append(cur_time)
    if (cur_time < 0):
      print("Wtf, why?")
      sys.exit(1)
    if (len(times) != len(Vs)):
      print("Mismatch lengths! ",len(times),len(Vs))
      sys.exit(1)
  fig, ax = plt.subplots()
  #print("Scattering ", len(times), len(Vs), len(I))
  #ax2 = ax.twinx()
  ax.plot(times,Vs,'b-',label='Cap. Voltage')
  #ax2.plot(times,I,'r-',label='Current')
  #ax.set_ylabel('Voltage (V)')
  #ax2.set_ylabel('Current (A)')
  E = 0
  for i in I:
    E = E + i*time_step*Vop
  avg_i = np.average(I)
  max_i = np.amax(I)
  print("Max time is: ",max(times))
  print("Max current is: ", max_i)
  print("Average current is: ", avg_i)
  plt.show()



def calc_sim(I,time_step,vcap=[]):
  #cap = Cap(37.5e-3,25/5)
  #cap = Cap(28e-3,25/4)
  #cap = Cap(22.5e-3,25/3)
  print("Running calc sim!")
  cap = Cap(15e-3,25/2)
  #cap = Cap(7e-3,25/1)
  Vmin = 1.81
  Vobj = VstartMin()
  Vobj.Vstart = vcap[0,1]
  print("Starting at: ",vcap[0,1])
  Vmax = 2.3
  Vop = 2.56
  # Reset cap values
  flag = 0
  Vs = []
  cur_time = 0
  times = []
  cap.v_internal = Vobj.Vstart
  cap.V=Vobj.Vstart
  cap.last_i = 0
  #print("Start loop ", Vobj.Vstart)
  Vs.append(cap.V)
  times.append(cur_time)
  for i in I:
    cur_time = cur_time + time_step
    new_V = cap.update_v(Vmax,0,Vop,i,get_eff(cap.V,i,efficiency_table_ps),time_step)
    #new_V = cap.update_v(Vmax,0,Vop,i,1,time_step)
    #print("New V is: ",new_V)
    Vs.append(new_V)
    #print(Vs)
    #print(times)
    times.append(cur_time)
    if (cur_time < 0):
      print("Wtf, why?")
      sys.exit(1)
    if (len(times) != len(Vs)):
      print("Mismatch lengths! ",len(times),len(Vs))
      sys.exit(1)
  print("Vmin actual is: ",Vobj.Vstart)
  fig, ax = plt.subplots()
  #print("Scattering ", len(times), len(Vs), len(I))
  #ax2 = ax.twinx()
  ax.plot(times,Vs,'b-',label='Cap. Voltage')
  #ax2.plot(times,I,'r-',label='Current')
  #ax.set_ylabel('Voltage (V)')
  #ax2.set_ylabel('Current (A)')
  E = 0
  for i in I:
    E = E + i*time_step*Vop
  avg_i = np.average(I)
  max_i = np.amax(I)
  print("Max time is: ",max(times))
  print("Max current is: ", max_i)
  print("Average current is: ", avg_i)
  naive_min = np.sqrt(2*E/cap.cap + Vmin**2) 
  naive_better_min = np.sqrt(2*E/cap.cap + (Vmin + avg_i*cap.r)**2)
  conservative_estimate = np.sqrt(2*E/cap.cap + (Vmin + max_i*cap.r)**2)
  print("Naive estimate duh: ",naive_min," ",100*(Vobj.Vstart - naive_min)/(Vmax -
  Vmin),"% difference")
  print("ESR with avg: ",naive_better_min," ",100*(Vobj.Vstart -
  naive_better_min)/(Vmax - Vmin),"% difference")
  print("Conservative: ",conservative_estimate," ",100*(Vobj.Vstart -
  conservative_estimate)/(Vmax - Vmin),"% difference")
  if len(vcap) > 0:
    #Pad new vcap
    actual_vs = vcap[:,1]
    if len(actual_vs) < len(times):
      time_diff = len(times) - len(actual_vs)
      new_times = times[0:-time_diff]
    else:
      new_times = times
    ax.plot(new_times,actual_vs,'k-',label='Actual Vcap')

  ax.legend(loc='upper center')
  #ax2.legend(loc='upper right')
  plt.savefig('real_and_sim_cap_traces.png')
  plt.show()

def calc_min(I,time_step,vcap=[]):
  #cap = Cap(37.5e-3,25/5)
  #cap = Cap(28e-3,25/4)
  #cap = Cap(22.5e-3,25/3)
  cap = Cap(15e-3,25/2)
  #cap = Cap(7e-3,25/1)
  Vmin = 1.81
  done = False
  Vobj = VstartMin()
  Vmax = 2.3
  Vop = 2.56
  while done == False:
    # Reset cap values
    flag = 0
    Vs = []
    cur_time = 0
    times = []
    cap.v_internal = Vobj.Vstart
    cap.V=Vobj.Vstart
    cap.last_i = 0
    #print("Start loop ", Vobj.Vstart)
    for i in I:
      #new_V = cap.update_v(Vmax,0,Vop,i,get_eff(cap.V,i,efficiency_table_ps),time_step)
      new_V = cap.update_v(Vmax,0,Vop,i,get_eff(Vmin,i,efficiency_table_ps),time_step)
      #new_V = cap.update_v(Vmax,0,Vop,i,1,time_step)
      #print("New V is: ",new_V)
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
  #print("Scattering ", len(times), len(Vs), len(I))
  ax2 = ax.twinx()
  ax.plot(times,Vs,'b-',label='Cap. Voltage')
  ax2.plot(times,I,'r-',label='Current')
  ax.set_ylabel('Voltage (V)')
  ax2.set_ylabel('Current (A)')
  E = 0
  for i in I:
    E = E + i*time_step*Vop
  avg_i = np.average(I)
  max_i = np.amax(I)
  print("Max time is: ",max(times))
  print("Max current is: ", max_i)
  print("Average current is: ", avg_i)
  naive_min = np.sqrt(2*E/cap.cap + Vmin**2) 
  naive_better_min = np.sqrt(2*E/cap.cap + (Vmin + avg_i*cap.r)**2)
  conservative_estimate = np.sqrt(2*E/cap.cap + (Vmin + max_i*cap.r)**2)
  print("Naive estimate: ",naive_min," ",100*(Vobj.Vstart - naive_min)/(Vmax -
  Vmin),"% difference")
  print("ESR with avg: ",naive_better_min," ",100*(Vobj.Vstart -
  naive_better_min)/(Vmax - Vmin),"% difference")
  print("Conservative: ",conservative_estimate," ",100*(Vobj.Vstart -
  conservative_estimate)/(Vmax - Vmin),"% difference")
  if len(vcap) > 0:
    #Pad new vcap
    actual_vs = vcap[:,1]
    if len(actual_vs) < len(times):
      time_diff = len(times) - len(actual_vs)
      new_times = times[0:-time_diff]
    else:
      new_times = times
    ax.plot(new_times,actual_vs,'k-',label='Actual Vcap')

  ax.legend(loc='upper center')
  ax2.legend(loc='upper right')
  plt.savefig('real_and_sim_cap_traces.png')
  plt.show()


def calc_min_forward(I,dt):
  L = 1.81
  C = .015
  R = 12.5
  V = 2.56
  I = np.flip(I)
  Vs = [] # Safe Vstarts squared
  Vdrops = []
  for count, i in enumerate(I):
    # TODO this cheats-- uses worst case eff all the time
    n = get_eff(L,i,efficiency_table_ps) 
    E = i*V*dt/n
    Vd = i*R/n
    Vdrops.append(Vd)
    if count == 0:
      new_Vs = 2*E/C + (L+Vd)**2
    else:
      if np.sqrt(Vs[count-1]) - Vd > L:
        new_Vs = 2*E/C + Vs[count-1]
      else:
        new_Vs = 2*E/C + (L+Vd)**2
    #print(np.sqrt(new_Vs))
    if (new_Vs < L**2):
      print("Error! value too low: ",new_Vs, count, i)
    Vs.append(new_Vs)
  fig, ax = plt.subplots()
  times = np.arange(0,len(I)*dt,dt)
  Vtrace = np.sqrt(Vs)
  Vtrace = np.flip(Vtrace)
  ax.plot(times,Vtrace)
  Vdrops = np.flip(Vdrops)
  ax2 = ax.twinx()
  ax2.plot(times,Vdrops,'-r')
  plt.title("calc min forward")
  plt.show()
  print("Vmin forward: ",np.sqrt(Vs[-1]))
  return np.sqrt(Vs[-1])

    


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
  print("Times1: ",len(vals))
  diffs = np.subtract(vals[:,1],vals[:,2])
  #diffs = np.subtract(vals[:,2],vals[:,1])
  I = np.divide(diffs,gain*shunt)
  dt = vals[1,0] - vals[0,0] 
  calc_min(I,dt)
  new_Vmin = calc_min_forward(I,dt)
  calc_sim_starting_point(I,dt,new_Vmin)
  sys.exit()
  if vals.shape[1] > 3:
    vals2 = np.column_stack((vals[:,0],vals[:,3]))
    print("Times2: ",len(vals2)) 
    calc_sim(I,dt,vals2)
  elif (len(sys.argv)>2):
    try:
      df2 = pd.read_csv(sys.argv[2], mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df2 = pd.read_csv(sys.argv[2], mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals2 = df2.values
    print("Times2: ",len(vals2)) 
    calc_sim(I,dt,vals2)
