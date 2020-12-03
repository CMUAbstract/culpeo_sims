import numpy as np
import pandas as pd
import sys
import math


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


def single_cycle(task_list, supercap, boost):
  supercap.v = boost.max
  successes = 0
  for task in task_list:
    esr_drop = task.i*supercap.r
    energy_drop = np.sqrt(2*task.i*task.t*boost.out)
    supercap.v = supercap.v - esr_drop - energy_drop
    if (supercap.v < boost.min):
      return [successes,1]
    else:
      supercap.v = supercap.v + esr_drop # Give back the drop when load is gone
      successes = successes + 1
  return [successes,0]


cpx = cap(7e-3,25)

def main():
  tasks = []
  for i in range(28):
    tasks.append(task(1e-3,10e-3,i))
  tasks.append(task(30e-3,100e-3,11))
  output_booster = booster(2.5, 1.8,2.6)
  cap_bank = cpx
  cap_bank.parallel(cpx)
  [fin, fail] = single_cycle(tasks,cap_bank,output_booster)
  print("Total finished: ", fin, " Total failed: ",fail)

if __name__ == "__main__":
  main()
