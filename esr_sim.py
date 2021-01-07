import numpy as np
import scipy
from scipy import stats
import pandas as pd
import sys
import math
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid.inset_locator import (inset_axes, InsetPosition,
                                                  mark_inset)


binary = '0'

def find_nearest(array,value):
  new_array = np.asarray(array)
  new_arr = new_array - value
  new_new_arr = np.absolute(new_arr)
  idx = new_new_arr.argmin()
  return array[idx]

class task:
  def __init__(self, current, time, priority):
    self.i = current #in amps
    self.t = time #in seconds
    self.p = priority


class cap:
  def __init__(self,capacity,esr,leak=0):
    self.cap = capacity
    self.r = esr
    self.v = 0
    self.leakage = leak
  def parallel(self,cap):
    self.cap = self.cap + cap.cap
    self.r = 1/(1/self.r + 1/cap.r)

#efficiency_table = {5.3 : {.1:.8, .5:.94, 1:.92},
#                    4.2 : {.1:.87, .5:.95, 1:.92},
#                    3.6 : {.1:.91, .5:.95, 1:.91},
#                    2.4 : {.1:.82, .5:.87, 1:.78}}
efficiency_table = {5.3 : {.1:1, .5:1, 1:1},
                    4.2 : {.1:1, .5:1, 1:1},
                    3.6 : {.1:1, .5:1, 1:1},
                    2.4 : {.1:1, .5:1, 1:1}}
class booster:
  def __init__(self,max_v,min_v,output_v):
    self.max = max_v
    self.min = min_v
    self.out = output_v
    self.eff = efficiency_table
  def get_eff(self,V_in,I_out):
    V = find_nearest([*self.eff.keys()],V_in)
    I = find_nearest([*self.eff[V].keys()],I_out)
    return self.eff[V][I]




#TODO we need a more robust model for efficiency, so far it's pretty stationary
class hardware:
  def __init__(self, power, voltage, TOPS):
    self.power = power
    self.perf = TOPS
    self.v = voltage
  def __repr__(self):
    return repr((self.power,self.perf))

# We'll measure "work" in tera-ops
# The baseline work is set for MobileNet v1, based on the Edge TPU stats
# available here: https://coral.ai/docs/edgetpu/benchmarks/ , assuming that the
# tpu was running at 4 TOPS
def multi_hw_inf(cap, boost, hw_list, work=1000):
  #Order hw by power
  work_start = work
  hw_list = sorted(hw_list, key=lambda hw: hw.perf, reverse=True)
  #Start running on first hw
  cap.v = boost.max
  fin = 0
  run_time = 0
  hw_used = 0
  work_finished = 0
  for counter,hw in enumerate(hw_list):
    hw_used = hw_used + 1
    #Get current draw
    i = hw.power/hw.v
    #Take ESR hit
    esr_drop = i*cap.r
    #Figure out how long we can run for, is it enough to finish?
    #TODO factor in power burnt over esr
    rt_left = .5*cap.cap*((cap.v**2-(boost.min+esr_drop)**2))/hw.power
    w_left = work/hw.perf
    if rt_left > w_left:
      #Done
      fin = 1
      print("Done all! ", counter)
      run_time = run_time + w_left
      work_finished = work_start
      if counter == 0:
        tpu_work = work_finished
      break
    #If we're about to die,
    else:
      #Turn off hw and turn on next
      if (rt_left < 0):
        print("Can't run:",counter)
        return 1
        break
      work = work - rt_left *hw.perf
      work_finished = rt_left*hw.perf + work_finished
      if counter == 0:
        tpu_work = work_finished
      run_time = run_time + rt_left
      # Apply drop due to energy extracted
      E_delta = hw.power*rt_left
      cap.v = np.sqrt(cap.v**2 - 2*E_delta/cap.cap)
      if (cap.v < boost.min+esr_drop):
        print("Error calculating tpu rt", counter)
        print("\t",cap.v," vs ",boost.min + esr_drop)
  #Repeat until workload is done or cap is exhausted
  print("Work finished: ",work_finished," in time ",run_time ," vs tpu ", tpu_work)
  return (work_finished/tpu_work)

def single_cycle(task_list, supercap, boost):
  supercap.v = boost.max
  successes = 0
  for task in task_list:
    esr_drop = task.i*supercap.r
    energy_drop = task.i*task.t*boost.out
    esr_burn_drop = (task.i**2)*supercap.r*task.t
    supercap.v = np.sqrt((supercap.v-esr_drop)**2 \
      -2*(energy_drop+esr_burn_drop)/supercap.cap)
    if (supercap.v < boost.min):
      return [successes,1]
    else:
      supercap.v = supercap.v + esr_drop # Give back the drop when load is gone
      successes = successes + 1
  return [successes,0]


# Swaps position of single expensive tasks from first to last, finds how many
# compute tasks can be performed in each instance
def compare_compute( supercap, boost, task_radio=task(100e-3,300e-3,0),\
  task_compute=task(1e-3,10e-3,0)):
  count = 0
  #print("Checking cap with ESR: ",supercap.r)
  max_tasks = .5*supercap.cap(boost.max**2-boost.min**2)/\
    (task_compute.i*boost.out*task.t)
  count = max_tasks
  while True:
    tasks = []
    tasks.append(task_radio)
    #TODO re-jigger as a binary search or something
    for i in range(count):
      tasks.append(task_compute)
    [successes, fails] = single_cycle(tasks,supercap,boost)
    if fails == 1:
      break
    else:
      count = count + 1
  #print("Finished: ",count - 1, " running before")
  before = count - 1
  count = 0
  while True:
    tasks = []
    for i in range(count):
      tasks.append(task_compute)
    tasks.append(task_radio)
    [successes, fails] = single_cycle(tasks,supercap,boost)
    if fails == 1:
      break
    else:
      count = count + 1
  #print("Finished: ",count - 1, " running after")
  after = count - 1
  return [before, after]

def search_esr_cap_numeric(esr_start, esr_stop,cap_size_start,cap_size_stop):
  esrs = np.logspace(esr_start,esr_stop, num=100)
  vals = np.logspace(cap_size_start, cap_size_stop,num=100)
  boost = booster(3.3,1.8,2.5)
  diffs = np.zeros((len(esrs),len(vals)))
  for i,esr in enumerate(esrs):
    print("Checking i,esr: ",i,esr)
    for j,val in enumerate(vals):
      #print("Checking val: ",val)
      dut = cap(val,esr)
      [before,after] = compare_compute_numeric(dut,boost)
      if after > 0 and before > 0:
       diffs[i,j] = before/after
       if binary == 1:
         if before/after > 10:
           diffs[i,j] = 1
         elif before/after > 5:
           diffs[i,j] = .75
         elif before/after > 2:
           diffs[i,j] = .5
         elif before/after > 1.2:
           diffs[i,j] = .25
         else:
          diffs[i,j] = .1
      elif before > 0 and after < 0:
        diffs[i,j] = 0
      else:
        diffs[i,j] = -1 #if neither can finish
      #TODO: create map/tuples of esr,size,ordering diff
  x, y = np.meshgrid(esrs,vals)
  plt.pcolormesh(x,y,diffs.T)
  plt.xlabel("ESR Ohms")
  plt.ylabel("Cap size (F)")
  plt.colorbar()
  plt.savefig("esr_capacity_shmoo.png")
  plt.show()
  calc_diffs = diffs[diffs > 0]
  geomean = scipy.stats.mstats.gmean(calc_diffs)
  print("Geomean improvement is: ",geomean)


def search_esr_cap(esr_start, esr_stop,cap_size_start,cap_size_stop):
  esrs = np.logspace(esr_start,esr_stop, num=25)
  vals = np.logspace(cap_size_start, cap_size_stop,num=25)
  boost = booster(5.5,2.0,3.3)
  diffs = np.zeros((len(esrs),len(vals)))
  for i,esr in enumerate(esrs):
    print("Checking i,esr: ",i,esr)
    for j,val in enumerate(vals):
      print("Checking val: ",val)
      dut = cap(val,esr)
      [before,after] = compare_compute(dut,boost)
      if after > 0 and before > 0:
       diffs[i,j] = before/after
      elif before > 0 and after < 0:
        diffs[i,j] = 0
      else:
        diffs[i,j] = -1 #if neither can finish
      #TODO: create map/tuples of esr,size,ordering diff
  x, y = np.meshgrid(esrs,vals)
  plt.pcolormesh(x,y,diffs.T)
  plt.xlabel("ESR Ohms")
  plt.ylabel("Cap size (F)")
  plt.colorbar()
  plt.savefig("esr_capacity_shmoo.png")
  plt.show()

cpx = cap(7e-3,25)
murata_small = cap(220e-3,300e-3)
murata_giant = cap(1,40e-3)
kemet = cap(5.6,600e-3)

cpx2 = cap(7e-3,2*25)
murata_small2 = cap(220e-3,2*300e-3)
murata_giant2 = cap(1,2*40e-3)
kemet2 = cap(5.6,2*600e-3)

capy_booster = booster(2.5,1.8,2.6)
artibeus_booster = booster(5.5,2.0,3.3)
bigger_capy_booster = booster(4.2,2.0,2.6)

def main():
  # Capy compare
  cap_bank = cpx
  cap_bank.parallel(cpx)
  print("Capy config")
  compare_compute_numeric(cap_bank,capy_booster)
  print("Artibeus config")
  compare_compute_numeric(kemet, artibeus_booster)
  print("Capy++ config")
  compare_compute_numeric(murata_small,bigger_capy_booster)

  cap_bank2 = cpx2
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  print("Capy2 config")
  compare_compute_numeric(cap_bank2,capy_booster)
  print("Artibeus2 config")
  compare_compute_numeric(kemet2, artibeus_booster)
  print("Capy2++ config")
  compare_compute_numeric(murata_small2,bigger_capy_booster)

def make_esr_capacity_shmoo():
  search_esr_cap(0, 1, -2, -1)
  cap_bank = cap(30e-3,8)
  [before, after] = compare_compute(cap_bank,artibeus_booster)
  print("Befor: ",before," After: ", after);


edge_tpu = hardware(2,1.8,4)
a53_quad = hardware(.75,1.8,.06)
restricted_artibeus = booster(5.5,2.5,3.3)
nr_artibeus = booster(5.5,2.0,3.3)
beefy_capy = booster(3.3,1.8,2.6)

def search_hw(power_start, power_stop, perf_start, perf_stop):
  powers=np.logspace(power_start, power_stop, num=50)
  perfs =np.logspace(perf_start, perf_stop, num=50)
  works = np.zeros((len(powers),len(perfs)))
  dworks = []
  dgops = []
  for i,power in enumerate(powers):
    print("Checking power: ",power,i)
    for j,perf in enumerate(perfs):
      print("Checking perf:", perf,j)
      test_board = []
      test_board.append(edge_tpu)
      dut = hardware(power,1.8,perf)
      test_board.append(dut)
      works[i,j] = multi_hw_inf(kemet,restricted_artibeus,test_board)
      if binary == 1:
        if works[i,j] > 1.5:
          works[i,j] = 1
        elif works[i,j] > 1.2:
          works[i,j] = .75
        elif works[i,j] > 1.1:
          works[i,j] = .5
        else:
          works[i,j] = 0
      print("\tchange: ",works[i,j])
      dworks.append(works[i,j])
      dgops.append((perf*10e2)/power)
  x,y = np.meshgrid(powers,perfs)
  #print("here")
  plt.pcolormesh(x,y,works.T,cmap='Blues')
  #print("here2")
  #print(powers)
  #print(perfs)
  #print(works)
  plt.xlabel("Backup device power (W)")
  plt.ylabel("Backup device perf (TOPS)")
  plt.colorbar()
  plt.savefig("hardware_inf.png")
  plt.close()
  plt.scatter(dgops,dworks)
  plt.ylabel("Normalized work with backup")
  plt.xlabel("Gops/W")
  plt.savefig("gop_vals.png")
  print(len(dgops), len(dworks))
  print(max(perfs), max(powers))
  plt.show()


def search_hw_a53(power_start, power_stop, perf_start, perf_stop):
  powers=np.logspace(power_start, power_stop, num=50)
  perfs =np.logspace(perf_start, perf_stop, num=50)
  works = np.zeros((len(powers),len(perfs)))
  dworks = []
  dgops = []
  for i,power in enumerate(powers):
    print("Checking power: ",power,i)
    for j,perf in enumerate(perfs):
      print("Checking perf:", perf,j)
      test_board = []
      test_board.append(a53_quad)
      dut = hardware(power,1.8,perf)
      test_board.append(dut)
      works[i,j] = multi_hw_inf(kemet,restricted_artibeus,test_board, work=1000)
      if binary == 1:
        if works[i,j] > 1.5:
          works[i,j] = 1
        elif works[i,j] > 1.2:
          works[i,j] = .75
        elif works[i,j] > 1.1:
          works[i,j] = .5
        else:
          works[i,j] = 0
      print("\tchange: ",works[i,j])
      dworks.append(works[i,j])
      dgops.append((perf*10e2)/power)
  x,y = np.meshgrid(powers,perfs)
  #print("here")
  plt.pcolormesh(x,y,works.T,cmap='Blues')
  #print("here2")
  #print(powers)
  #print(perfs)
  #print(works)
  plt.xlabel("Backup device power (W)")
  plt.ylabel("Backup device perf (TOPS)")
  plt.colorbar()
  plt.savefig("hardware_inf.png")
  plt.close()
  plt.scatter(dgops,dworks)
  plt.ylabel("Normalized work with backup")
  plt.xlabel("Gops/W")
  plt.savefig("gop_vals.png")
  print(len(dgops), len(dworks))
  print(max(perfs), max(powers))
  plt.show()

def cap_voltage(tasks,supercap,boost,dt=.001):
  #Energy that can't be accessed
  E_og = .5*supercap.cap*(boost.max**2 - boost.min**2)
  # Need to integrate through cap voltage as it declines, figure out what max t
  # is, then back out work performed
  E_used = 0
  V_in = boost.max
  shifted_start = V_in
  #V_in = boost.max
  t = 0
  times = []
  voltages = []
  times.append(t)
  voltages.append(V_in)
  flag = 0
  for count,task in enumerate(tasks):
    t_task_start = t
    I = task.i
    print("Task #",count)
    while t - t_task_start < task.t:
      n = boost.get_eff(V_in,I)
      P_inst = I*boost.out/n
      #P_esr = 0
      P_esr = supercap.r*(boost.out*task.i/(n*V_in))**2
      E_step = (P_inst + P_esr)*dt
      E_used = E_used + E_step
      V_next = np.sqrt(V_in**2 - 2*E_step/supercap.cap)
      V_in = V_next 
      #print("V_in: ",V_in,"n is ",n,"E_step: ",E_step, "E_used: ",E_used)
      t = t + dt
      times.append(t)
      voltages.append(V_in - supercap.r*task.i)
      if (V_in < boost.min + supercap.r*task.i):
        flag = 1
        print("Out of energy! leaving!")
        break
    if flag != 0:
      break
  return [times,voltages]

def work_done(hw,supercap,boost,dt=.001):
  #Energy that can't be accessed
  E_og = .5*supercap.cap*(boost.max**2 - boost.min**2)
  # Need to integrate through cap voltage as it declines, figure out what max t
  # is, then back out work performed
  I = hw.power/hw.v
  E_used = 0
  V_in = boost.max
  shifted_start = V_in
  #V_in = boost.max
  t = 0
  print("Starting at ", V_in," comparing to ",boost.min + supercap.r*I)
  while V_in > (boost.min + supercap.r*hw.power/hw.v):
    n = boost.get_eff(V_in,I)
    P_inst = hw.power/n
    #P_esr = 0
    P_esr = supercap.r*(hw.power/(n*V_in))**2
    E_step = (P_inst + P_esr)*dt
    E_used = E_used + E_step
    V_next = np.sqrt(V_in**2 - 2*E_step/supercap.cap)
    V_in = V_next 
    #print("V_in: ",V_in,"n is ",n,"E_step: ",E_step, "E_used: ",E_used)
    t = t + dt
  print("Ran for: ",t, "Used ",E_used,"final v_in: ",V_in)
  print("E left: ",E_og-E_used)
  print("E expected used: ",.5*supercap.cap*(shifted_start**2 - boost.min**2))
  work = t*hw.perf
  return work

def ideal_work(I_start, I_stop):
  currents = np.logspace(I_start,I_stop,num=25)
  boost = booster(5.5,2.0,3.3)
  eff = .5 # as measured in TOPS/W
  v = 1.8
  test_cap = cap(5.6,.6)
  ideal_cap = cap(test_cap.cap,0)
  power = []
  work = []
  ideal_work = []
  for i,current in enumerate(currents):
    dut_pow = current*v
    power.append(dut_pow)
    perf = eff*dut_pow
    dut = hardware(dut_pow,v,perf)
    work.append(work_done(dut,test_cap,boost))
  for i,current in enumerate(currents):
    dut_pow = current*v
    perf = eff*dut_pow
    dut = hardware(dut_pow,v,perf)
    ideal_work.append(work_done(dut,ideal_cap,boost))
  plt.plot(power,work,label='Non-ideal')
  plt.plot(power,ideal_work, label='ideal')
  plt.legend()
  plt.xlabel("Power (W)")
  plt.ylabel("Work (TOPS)")
  title_str = "Booster config:"+str(boost.max)+","+str(boost.min)+\
  "\nCap size:"+str(5.6)+",HW eff:"+str(eff)
  plt.title(title_str)
  plt.savefig("ideal_work.png")
  plt.show()



def compare_compute_numeric(supercap,boost, task_radio=task(110e-3,130e-3,0),\
  task_compute=task(1e-3,10e-3,0)):
  #Figure out how much work we can do if we run the high energy task first
  Eh = task_radio.i*boost.out*task_radio.t
  El = task_compute.i*boost.out*task_compute.t
  Il = task_compute.i
  Ih = task_radio.i
  C = supercap.cap
  R = supercap.r
  #Do checks n'at for running the high energy task first
  term0 = boost.max**2 - 2*Eh/C
  Vendh = np.sqrt(term0)
  if (term0 < 0) or (Vendh < boost.min+Ih*R):
    print("Error! Eh is too big")
    return [0,0]
  n_before = .5*C*(Vendh**2 - (boost.min+Il*R)**2)/El
  n_before =  np.floor(n_before)
  #print("N before is ",n_before)
  #Now do the calc for the low energy task first
  term1 = boost.max**2 - (boost.min+Ih*R)**2 - 2*Eh/C
  if term1 < 0:
    print("Error! Eh is too big!")
    return [0,0]
  n_after = term1*.5*C/El
  n_after = np.floor(n_after)
  #print("N after is ",n_after)
  return [n_before, n_after]




if __name__ == "__main__":
  if len(sys.argv) > 1:
    binary = int(sys.argv[1])
  #main()
  boost = booster(3.3,1.8,2.5)
  #search_esr_cap_numeric(-2,1,-2,-1)
  dut = cap(.021,8.3)
  [before,after] = compare_compute_numeric(dut,boost)
  print("Before: ",before," after: ",after)
  task_list = []
  #task_list.append(task(110e-3,130e-3,0))
  task_list.append(task(1e-3,50e-3,0))
  task_list.append(task(1e-3,.7,0))
  #task_list.append(task(1e-3,18.1,0))
  task_list.append(task(110e-3,100e-3,0))
  #task_list.append(task(1e-3,10e-3,0))
  [times,voltages]=cap_voltage(task_list,dut,boost,dt=.001)
  task_list = []
  task_list.append(task(1e-3,50e-3,0))
  task_list.append(task(110e-3,100e-3,0))
  task_list.append(task(1e-3,18,0))
  [times1,voltages1]=cap_voltage(task_list,dut,boost,dt=.001)
  fig,ax1=plt.subplots()
  ax1.set_xlim(left=0,right=1.0)
  #plt.xlim(left=0,right=2)
  ax1.plot(times,voltages,'r',label="Expensive task second")
  ax1.plot(times1,voltages1,'b',label="Expensive task first")
  ax1.plot(times1,[3.3]*len(times1),'k--',times1,[1.8]*len(times1),'k--')
  ax1.set_ylabel("Capacitor Output Voltage (V)")
  ax1.set_xlabel("Time (s)")
  ax1.legend(bbox_to_anchor=[.1,1],ncol=2)
  #ax2 = plt.axes([0,0,1,1])
  #ip = InsetPosition(ax1,[.55,.45,.4,.4])
  #ax2.set_axes_locator(ip)
  #mark_inset(ax1, ax2, loc1=2, loc2=4, fc="none", ec='0.5')
  #ax2.plot(times,voltages,'r',label="Expensive task second")
  #ax2.plot(times1,voltages1,'b',label="Expensive task first")
  #ax2.set_xlim(0,1)
  #ax2.set_xticks(np.arange(0,1,.25))
  #ax2.set_xticklabels(ax2.get_xticks(), backgroundcolor='w')
  ax1.annotate('Init. Code', xy=(.02,3.3),  xycoords='data',
            xytext=(.02,3.6), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='top',
            )
  ax1.annotate('ESR Drop', xy=(.05,3.0),  xycoords='data',
            xytext=(.2,3.0), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
  ax1.annotate('ESR Drop', xy=(.75,3.0),  xycoords='data',
            xytext=(.9,3.0), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
  ax1.annotate('LoRa\nPkt.', xy=(.13,2.0),  xycoords='data',
            xytext=(.04,1.88), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
  ax1.annotate('LoRa\nPkt.', xy=(.82,2.0),  xycoords='data',
            xytext=(.68,2.0), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='center',
            )
  ax1.annotate('Compute', xy=(.6,3.25),  xycoords='data',
            xytext=(.6,3.0), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='top',
            )
  ax1.annotate('Compute', xy=(.6,2.75),  xycoords='data',
            xytext=(.6,2.4), textcoords='data',
            arrowprops=dict(facecolor='black', shrink=0.05),
            horizontalalignment='center', verticalalignment='top',
            )
  ax1.annotate('Energy\nStill\nAvailable', xy=(1,2.7),  xycoords='data',
            xytext=(.9,2.55), textcoords='data',color='green',
            arrowprops=dict(facecolor='green', shrink=0.05),
            horizontalalignment='center', verticalalignment='top',
            )
  ax1.annotate('Energy\nDepleted', xy=(.85,1.8),  xycoords='data',
            xytext=(.87,2.07), textcoords='data',color='red',
            arrowprops=dict(facecolor='red', shrink=0.05),
            horizontalalignment='left', verticalalignment='center',
            )
  ratio = 1/2
  xleft, xright = ax1.get_xlim()
  ybottom, ytop = ax1.get_ylim()
  ax1.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.savefig("cap_voltage.png",bbox_inches='tight')
  plt.show()
  #coral = []
  #coral.append(edge_tpu)
  #coral.append(hardware(.01,1.8,.25))
  #work_done(edge_tpu,kemet,restricted_artibeus)
  #bank = kemet
  #bank.parallel(kemet)
  #work = multi_hw_inf(bank,restricted_artibeus,coral)
  #print(work)
  #print(work)
  #search_hw(-2,-1,-2,-1)
  #print(binary)
  #ideal_work(-1,.2)
  #search_hw_a53(-2,0,-3,-2)
  #~10% improvement for kemet2 + restricted artibeus with divider=4
  #~28% improvement for kemet2 with beefy_capy
  cap_bank = cpx
  cap_bank.parallel(cpx)
  cap_bank.parallel(cpx)
  cap_bank.parallel(cpx)
  #cap_bank.parallel(cpx)
  #cap_bank.parallel(cpx)
  #cap_bank.parallel(cpx)
  divider = 1
  perf_divider = 1
  divider2 =4
  perf_divider2 = 3
  divider3 = 10
  perf_divider3 = 12
  test_board = []
  dut = hardware(a53_quad.power/divider, 1.8,a53_quad.perf/perf_divider)
  test_board.append(dut)
  dut = hardware(a53_quad.power/divider2, 1.8,a53_quad.perf/perf_divider2)
  test_board.append(dut)
  # New divider
  dut = hardware(a53_quad.power/divider3, 1.8,a53_quad.perf/perf_divider3)
  test_board.append(dut)
  work1 = multi_hw_inf(murata_small,beefy_capy,test_board,work=.25)
  print("Work diff is: ",work1, "for power:",divider)
  work1 = multi_hw_inf(cap_bank,beefy_capy,test_board,work=.25)
  print("Work diff is: ",work1, "for power:",divider)
  work1 = multi_hw_inf(kemet,nr_artibeus,test_board,work=10)
  print("Work diff is: ",work1, "for power:",divider)

