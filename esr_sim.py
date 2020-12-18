import numpy as np
import scipy
from scipy import stats
import pandas as pd
import sys
import math
import pickle
import matplotlib.pyplot as plt

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
  def __init__(self,capacity,esr):
    self.cap = capacity
    self.r = esr
    self.v = 0
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
      run_time = run_time + w_left
      work_finished = work
      if counter == 0:
        tpu_work = work_finished
        print("Done all!\r\n")
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
        print("Error calculating tpu rt")
  #Repeat until workload is done or cap is exhausted
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
a53_quad = hardware(.25,1.8,.1)
restricted_artibeus = booster(5.5,2.5,3.3)

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



def compare_compute_numeric(supercap,boost, task_radio=task(100e-3,300e-3,0),\
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
  main()
  #search_esr_cap_numeric(-2,1,-2,-1)
  coral = []
  coral.append(edge_tpu)
  coral.append(hardware(.01,1.8,.25))
  #work_done(edge_tpu,kemet,restricted_artibeus)
  #bank = kemet
  #bank.parallel(kemet)
  #work = multi_hw_inf(bank,restricted_artibeus,coral)
  #print(work)
  #print(work)
  #search_hw(-2,-1,-2,-1)
  #print(binary)
  ideal_work(-1,.2)

