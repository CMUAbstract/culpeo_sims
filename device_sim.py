import numpy as np
from enum import Enum
import sys
import math
import matplotlib.pyplot as plt
import json

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
  def update_v(self,v_in,i_in,v_out,i_out,n,dt):
    e_step = (v_in*i_in - v_out*i_out/n)*dt
    term1 = self.v_internal**2
    term2 = 2*e_step/self.cap
    if term2 > 0 or term1 > abs(term2):
      self.v_internal = np.sqrt(term1 + term2)
    else:
      self.v_internal = 0
    if (self.v_internal > v_in):
      self.v_internal = v_in
    if (self.v_internal <= 0):
      self.v_internal = 0
    i_net = i_in - i_out
    self.V = self.v_internal + ( i_net*self.r)
    #self.V = self.v_internal - (self.last_i - i_net)*self.r #TODO holds for charging?
    #print("Vals after: ", e_step,i_net,self.v_internal,self.V)
    if (self.V > v_in):
      self.V = v_in
      self.last_i = 0
    elif (self.V <= 0):
      self.V = 0
      self.last_i = 0
    else:
      self.last_i = i_net
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
  def update(self,v_in,i_in,v_out,i_out,n,dt):
    '''Updates the capacitor voltage and confirms that we're still in bounds for
    the input and output boosters.  Returns the current produced by the
    output booster, this is subject to change... We may need to work in the
    input booster too'''
    V = self.cap.update_v(v_in,i_in,v_out,i_out,n,dt)
    if (self.cap.V < self.boost.min):
      return V,0
    else:
      return V,i_out

class OperatingPoint:
  def __init__(self,v,i,freq):
    self.v = v
    self.i = i
    self.freq = freq


slow = OperatingPoint(2.5,.001,8e6)
medium = OperatingPoint(2.5,.002,12e6)
fast = OperatingPoint(2.5,.004,16e6)

class Mcu:
  '''Produces current trace that the power system handles by keeping back of
  software tasks to run and possible hardware modes'''
  def __init__(self):
    self.uno_tsks = [] #unordered tasks
    self.o_tsks = [] #ordered tasks
    self.evts = [] #preempting events
    self.eff_point = {slow,medium,fast} #TODO not portable, need freq earlier
  def add_unordered(self,new_tsk):
    self.uno_tsks.append(new_tsk)
  def add_ordered(self,new_tsk):
    self.o_tsks.append(new_tsk)
  def add_event(self,new_evt):
    self.evts.append(new_evt)
  def load_program(self,prog):
    #TODO need a way to compose ops into tasks
    for op in prog.ops:
      self.add_ordered(op)
  def prog_complete(self):
    print("lengths: ", len(self.o_tsks))
    if self.uno_tsks or self.o_tsks or self.evts:
      return False
    else:
      return True


# Selects the next operation to run based on input from the booster/capacitor
# hardware status and the mcu's software status
class Scheduler:
  ''' Selects the next operation to run based on input from the booster/capacitor
      hardware status and the mcu's software status'''
  def __init__(self,policy,power_sys,mcu):
    self.policy = policy
    self.power = power_sys
    self.mcu = mcu
    self.recharging = False
  def select_work(self):
    # Check our voltage
    print("Selecting work! ", self.power.cap.V)
    # Currently implementing a full recharge policy, change/add extra cases here
    # if we're not doing a full recharge
    if self.power.cap.V <= self.power.boost.min or (self.power.cap.V <
      self.power.chrg.max and self.recharging == True):
      next_tsk = self.schedule_rechrg()
      self.recharging = True
      return next_tsk
    if self.power.cap.V >= self.power.chrg.max or self.recharging == False:
      next_tsk = self.schedule_op()
      self.recharging = False
      return next_tsk
    else:
      next_tsk = self.schedule_rechrg
    return next_tsk
 
  def schedule_op(self):
    '''Selects the next work to do'''
    return self.mcu.o_tsks.pop(0) # Scheduling policy for now...

  def schedule_rechrg(self):
    print("Adding rechg!")
    rechrg = Operation(OpTypes.RECHARGE)
    rechrg.times = [10] #TODO determine recharge using scheduling policy
    rechrg.i_load = [0]
    return rechrg
 
  def reschedule(self,op):
    '''Controls policy for rescheduling work after a power failure'''
    # We first check if the work is atomic or not
    if op.atomic:
      if op.fails < 2: #TODO this is just the policy for now
        self.mcu.o_tsks.insert(0,op) # Push back on front of queue
        return False # Still going
      else:
        # If we end up failing even after we start at the beginning, op is too
        # big
        return True
    else: #TODO only the policy for now
      self.mcu.o_tsks.insert(0,op) # Push back on front of queue

  def run_work(self,times,voltages,op):
    if op.atomic == True:
      finished, test_op = self.run_work_atomic(self.power,times,voltages,op)
    else:
      finished, test_op = run_work_interruptible(self.power,times,voltages,op)
    return finished, test_op

  def run_work_atomic(self,power,times,voltages,op):
    time = times[-1]
    fail_flag = 0
    for i, time_step in enumerate(op.times):
      if time_step > 1e-3:
        for j in np.arange(0,time_step,1e-3):
          dt = 1e-3
          V, i_out = power.update(power.chrg.max, power.chrg.i, power.boost.out,
            op.i_load[i],1,dt)
          time += dt
          times.append(time)
          voltages.append(V)
          #if at some point we run out of energy, indicate fail, recharge,
          #reschedule
          if V <= power.boost.min:
            fail_flag = 1
            break
      else:
        V, i_out = power.update(power.chrg.max, power.chrg.i, power.boost.out,
          op.i_load[i],1,time_step)
        time += time_step
        times.append(time)
        voltages.append(V)
        #if at some point we run out of energy, indicate fail, recharge,
        #reschedule
        if V <= power.boost.min:
          fail_flag = 1
      # Check if we made it through or not
      if fail_flag > 0:
        print("Fail!")
        # If we didn't make it, quit early and send back op along with False
        # completion
        op.fails += 1
        return False, op
    # If we made it here, fail flag shouldn't be on... send back true completion
    # with op for convenience
    return True, op

  def run_work_interruptible(power,times,voltages,op):
    print("Need to implement")
    return True, op


class OpTypes(Enum):
  MEMORY = 1
  COMPUTE = 2
  PERIPH = 3
  RECHARGE = 4

class PolicyTypes(Enum):
  BASIC = 1
  LOAD_AWARE = 2
  EVTS_FIRST = 3

class QueueTypes(Enum):
  ORDERED = 1
  UNORDERED = 2
  EVENT = 3

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
    self.times = []
    self.i_load = 0
    self.atomic = True # TODO change for each optype
    self.fails = 0
    self.queue = QueueTypes.ORDERED
    self.progress = 0 # Used differently by the different types

class MemOp(Operation):
  ''' Defines memory bound operations in terms of memory access times '''
  def __init__(self,tsk_type,count,latency,i_load):
    super().__init__(tsk_type)
    self.count = count
    self.latency = latency
    self.i_load = i_load
    self.times = [latency] * count
    self.i_load = [i_load] * count

class CompOp(Operation):
  ''' Defines compute bound operation '''
  def __init__(self,tsk_type,instr_count,mcu_freq,mcu_i):
    super().__init__(tsk_type)
    self.instr_count = instr_count
    self.times = [instr_count/mcu_freq] * 1
    self.i_load = [mcu_i] * 1

class PeriphOp(Operation):
  ''' Defines peripheral operation '''
  def __init__(self,tsk_type,latencies,i_loads):
    super().__init__(tsk_type)
    self.times = latencies
    self.i_load = i_loads

class Program:
  def __init__(self):
    self.ops = []
  def add_ops(self,new_ops):
    self.opps.append(new_ops)
  def build(self,prog_txt,mcu_freq,mcu_i):
    prog_file = open(prog_txt)
    json_prog = json.load(prog_file)
    # Split json array
    for op in json_prog:
    # For each object, check the type
    #Translate into Operation type
      if op["type"] == 1:
        #MemOp
        new_op = MemOp(op["type"],op["count"],op["latency"],op["i_load"])
      elif op["type"] == 2:
        #CompOp
        new_op = CompOp(op["type"],op["instr_count"],mcu_freq,mcu_i)
      else:
        #PeriphOp
        new_op = PeriphOp(op["type"],op["times"],op["i_loads"])
 
      self.ops.append(new_op)


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
    self.mcu.load_program(self.prog)
    print("Running program")
    # Charge up capacitor,
    #self.times.append(0)
    time = 0
    while (self.power.cap.V < self.power.chrg.max - .1):
      #TODO get efficiency for real
      dt = 1e-3
      V, i_dummy = self.power.update(self.power.chrg.max, self.power.chrg.i,0,0,1,dt)
      time += dt
      self.times.append(time)
      self.voltages.append(V)
    print("charged cap: ",self.power.cap.V, self.mcu.prog_complete())
    fails = 0
    while self.mcu.prog_complete() == False:
      # Use scheduler to pick next task
      next_tsk = self.sched.select_work()
      print(next_tsk)
      # For each op in each task, extract energy from cap
      finished, op = self.sched.run_work(self.times,self.voltages,next_tsk)
      if finished == False:
        halted = self.sched.reschedule(op)
        if halted:
          print("No progress!")
          break;
    print("Done program")
  def plot_program(self):
    ''' Plot voltage vs time produced while running a program '''
    fig, ax = plt.subplots()
    ax.plot(self.times,self.voltages,color='#6baed6')
    plt.show()
    plt.savefig("program.pdf")

artyBoost = Booster(5.5,2.5,3.3)
artyChrg = Charger(5.5,.025)
kemet = Cap(5.6,.6)
artyPowerSys = PowerSys(artyChrg,kemet,artyBoost)
msp430 = Mcu()
basic = Program()

if __name__ == "__main__":
  basic.build("program.json",8e6,1e-3)
  Arty = Device(artyPowerSys,msp430,PolicyTypes.BASIC,basic)
  Arty.run_program()
  Arty.plot_program()
