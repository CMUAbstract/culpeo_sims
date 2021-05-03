import numpy as np
from enum import Enum
import sys
import math
import matplotlib.pyplot as plt


class Cap:
  '''Supercapacitor representation'''
  def __init__(self,capacity,esr,leak=0):
    self.cap = capacity
    self.r = esr
    self.v_internal = 0 #Before ESR, i.e. right at the internal "ideal" cap
    self.V = 0 #After ESR, i.e. the voltage at the terminal
    self.leakage = leak
    self.last_i = 0
  def parallel(self,cap):
    self.cap = self.cap + cap.cap
    self.r = 1/(1/self.r + 1/cap.r)
  def update_v(self,p_out,p_in,dt):
    e_step = (p_in - p_out)*dt
    self.v_internal = np.sqrt(self.v_internal**2 + 2*e_step/self.cap)
    i_out = (p_in - p_out)/self.v_internal #TODO Double check approximation
    self.V = self.v_internal - (self.last_i - i_out)*self.r #TODO holds for charging?
    self.last_i = i_out
    return self.V


#efficiency_table = {5.3 : {.1:.8, .5:.94, 1:.92},
#                    4.2 : {.1:.87, .5:.95, 1:.92},
#                    3.6 : {.1:.91, .5:.95, 1:.91},
#                    2.4 : {.1:.82, .5:.87, 1:.78}}
efficiency_table = {5.3 : {.1:1, .5:1, 1:1},
                    4.2 : {.1:1, .5:1, 1:1},
                    3.6 : {.1:1, .5:1, 1:1},
                    2.4 : {.1:1, .5:1, 1:1}}
class Booster:
  '''Output booster representation, all initialization values in Volts'''
  def __init__(self,max_v,min_v,output_v):
    self.max = max_v
    self.min = min_v
    self.out = output_v
    self.eff = efficiency_table
  def get_eff(self,V_in,I_out):
    V = find_nearest([*self.eff.keys()],V_in)
    I = find_nearest([*self.eff[V].keys()],I_out)
    return self.eff[V][I]


class Charger:
  '''Input booster representation, should be improved with a charging profile'''
  def __init__(self,v,i):
    self.max = v #In Volts
    self.i = i #In Amps


class PowerSys:
  '''Holds all the data for the power system, allows us to determine current in
     and stuff like that'''
  def __init__(self,charger,cap,booster):
    self.chrg = charger
    self.boost = booster
    self.cap = cap

class Mcu:
  '''Produces current trace that the power system handles by keeping back of
  software tasks to run and possible hardware modes'''
  def __init__(self):
    self.uno_tsks = [] #unordered tasks
    self.o_tsks = [] #ordered tasks
    self.evts = [] #preempting events
  def add_unordered(self,new_tsk):
    self.uno_tsks.append(new_tsk)
  def add_ordered(self,new_tsk):
    self.o_tsks.append(new_tsk)
  def add_event(self,new_evt):
    self.evts.append(new_evt)


# Selects the next operation to run based on input from the booster/capacitor
# hardware status and the mcu's software status
class Scheduler:
  ''' Selects the next operation to run based on input from the booster/capacitor
      hardware status and the mcu's software status'''
  def __init__(self,policy,power_sys,mcu):
    self.policy = policy #TODO make this an enum
    self.sys = power_sys
    self.mcu = mcu
  def schedule_op():
    return mcu.uno_tsks.pop(0) # Scheduling policy for now...

class OpTypes(Enum):
  MEMORY = 1
  COMPUTE = 2
  PERIPH = 3

class PolicyTypes(Enum):
  BASIC = 1
  LOAD_AWARE = 2
  EVTS_FIRST = 3

class Operation:
  ''' Software operation that mcu will handle '''
  def __init__(self,tsk_type):
    self.type = tsk_type
    if tsk_type == OpTypes.MEMORY:
      self.scalable = False #TODO we can scale if memory system is flexible
    elif tsk_type == OpTypes.COMPUTE:
      self.scalable = True
    else:
      self.scalable = False
  def set_attribtutes(self):
    self.times = []
    self.i_load = 0

class MemOp(Operation):
  ''' Defines memory bound operations in terms of memory access times '''
  def set_attributes(self, count,latency,i_load):
    self.times = [latency] * count
    self.i_load = [i_load] * count

class CompOp(Operation):
  ''' Defines compute bound operation '''
  def set_atrributes(self,cycle_count, mcu_freq, mcu_i):
    self.times = [mcu_freq] * cycle_count
    self.i_load = [mcu_i] * cycle_count

class PeriphOp(Operation):
  ''' Defines peripheral operation '''
  def set_attributes(self,latencies,i_loads):
    self.times = latencies
    self.i_load = i_loads

class Program:
  def __init__(self):
    self.ops = []
  def add_ops(self,new_ops):
    self.opps.append(new_ops)

class Device:
  ''' Represents entire device '''
  def __init__(self,powersys,mcu,policy,program):
    self.power = powersys
    self.mcu = mcu
    self.sched = Scheduler(policy,powersys,mcu)
    self.prog = program # List of ops
    self.times = []
    self.voltages = []
  def run_program(self):
    ''' Execute the current program given the device setup '''
    print("Running program")
  def plot_program(self):
    ''' Plot voltage vs time produced while running a program '''
    fig, ax = plt.subplots()
    ax.plot(self.times,self.voltages,color='#6baed6')
    plt.show()
    plt.savefig("program.pdf",bbox_inches='tight')

artyBoost = Booster(5.5,2.5,3.3)
artyChrg = Charger(5.5,.1)
kemet = Cap(5.6,.6)
artyPowerSys = PowerSys(artyChrg,kemet,artyBoost)
msp430 = Mcu()
basic = Program()

if __name__ == "__main__":
  Arty = Device(artyPowerSys,msp430,PolicyTypes.BASIC,basic)
  Arty.run_program()
  Arty.plot_program()
