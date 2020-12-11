import numpy as np
import pandas as pd
import sys
import math
import pickle
import matplotlib.pyplot as plt

binary = '0'

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

class booster:
  def __init__(self,max_v,min_v,output_v):
    self.max = max_v
    self.min = min_v
    self.out = output_v

#TODO we need a model for current draw and booster efficiency tanking
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
def multi_hw_inf(cap, boost, hw_list, work=100):
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
    #print("hw power is ", hw.power)
    #Get current draw
    i = hw.power/hw.v
    #print("Current is: ",i)
    #Take ESR hit
    esr_drop = i*cap.r
    #print("Esr hit is: ",esr_drop)
    cap.v = cap.v - esr_drop
    #print("Cap v is : ", cap.v, "Cap.cap is:",cap.cap)
    #print("Boost min is: ",boost.min," hw power is ", hw.power)
    #Figure out how long we can run for, is it enough to finish? 
    rt_left = .5*cap.cap*((cap.v-boost.min)**2)/hw.power
    #print("Rt left is: ", rt_left)
    w_left = work/hw.perf
    #print("Work left is: ", w_left)
    if rt_left > w_left:
      #Done
      fin = 1
      run_time = run_time + w_left
      work_finished = work
      if counter == 0:
        tpu_work = work_finished
      break
    #If we're about to die,
    else:
      #Turn off hw and turn on next
      work = work - rt_left *hw.perf
      work_finished = rt_left*hw.perf + work_finished
      if counter == 0:
        tpu_work = work_finished
      run_time = run_time + rt_left
      # Remove load
      cap.v = cap.v + esr_drop
      # Apply drop due to energy extracted
      cap.v = cap.v - np.sqrt(2*hw.power*rt_left/cap.cap)
  #Repeat until workload is done or cap is exhausted
  #Report time to finish, final hw in use
  #print("Runtime is: ",run_time, "finished: ",fin)
  if binary != '0':
    if work_finished/tpu_work > 1.1:
      return 1
    else:
      return 0
  else:
    return (work_finished/tpu_work)

def single_cycle(task_list, supercap, boost):
  supercap.v = boost.max
  successes = 0
  for task in task_list:
    esr_drop = task.i*supercap.r
    energy_drop = np.sqrt(2*task.i*task.t*boost.out/supercap.cap)
    supercap.v = supercap.v - esr_drop - energy_drop
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
  while True:
    tasks = []
    tasks.append(task_radio)
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


def search_esr_cap(esr_start, esr_stop,cap_size_start,cap_size_stop):
  esrs = np.logspace(esr_start,esr_stop, num=25)
  vals = np.logspace(cap_size_start, cap_size_stop,num=25)
  boost = booster(5.5,2.0,3.3)
  diffs = np.zeros((len(esrs),len(vals)))
  for i,esr in enumerate(esrs):
    print("Checking i,esr: ",i,esr)
    for j,val in enumerate(vals):
      #print("Checking val: ",val)
      dut = cap(val,esr)
      [before,after] = compare_compute(dut,boost)
      if after > 0 and before > 0:
       diffs[i,j] = (before)/after
      else:
        diffs[i,j] = 0
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
  compare_compute(cap_bank,capy_booster)
  print("Artibeus config")
  compare_compute(kemet, artibeus_booster)
  print("Capy++ config")
  compare_compute(murata_small,bigger_capy_booster)

  cap_bank2 = cpx2
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  cap_bank2.parallel(cpx2)
  print("Capy2 config")
  compare_compute(cap_bank2,capy_booster)
  print("Artibeus2 config")
  compare_compute(kemet2, artibeus_booster)
  print("Capy2++ config")
  compare_compute(murata_small2,bigger_capy_booster)

def make_esr_capacity_shmoo():
  search_esr_cap(-2, 1, -2, -1)
  cap_bank = cap(30e-3,8)
  [before, after] = compare_compute(cap_bank,artibeus_booster)
  print("Befor: ",before," After: ", after);


edge_tpu = hardware(2,1.8,4)
a53_quad = hardware(.25,1.8,.1)
restricted_artibeus = booster(5.5,2.5,3.3)

def search_hw(power_start, power_stop, perf_start, perf_stop):
  powers=np.logspace(power_start, power_stop, num=25)
  perfs =np.logspace(perf_start, perf_stop, num=25)
  works = np.zeros((len(powers),len(perfs)))
  for i,power in enumerate(powers):
    print("Checking power: ",power,i)
    for j,perf in enumerate(perfs):
      print("Checking perf:", perf,j)
      test_board = []
      test_board.append(edge_tpu)
      dut = hardware(power,1.8,perf)
      test_board.append(dut)
      works[i,j] = multi_hw_inf(kemet2,restricted_artibeus,test_board)
  x,y = np.meshgrid(powers,perfs)
  print("here")
  plt.pcolormesh(x,y,works.T,cmap='Blues')
  print("here2")
  print(powers)
  print(perfs)
  print(works)
  plt.xlabel("Backup device power (W)")
  plt.ylabel("Backup device perf (TOPS)")
  plt.colorbar()
  plt.savefig("hardware_inf.png")




if __name__ == "__main__":
  make_esr_capacity_shmoo()
  #if len(sys.argv) > 1:
  #  binary = sys.argv[1]
  #coral = []
  #coral.append(edge_tpu)
  #coral.append(hardware(.25,1.8,.4))
  #work = multi_hw_inf(kemet,restricted_artibeus,coral)
  #print(work)
  search_hw(-2,0,-2,-1)
  print(binary)

