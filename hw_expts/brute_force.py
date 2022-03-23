# Script for brute forcing the vsafe values for each expt
# Rough idea is we start up at the Culpeo point, then (running a binary search)
# repeat until we find the smallest voltage that does not fail.
# Need to be +/- 5 ticks to hit this (not sure if we can actually hit this)



# Software setup instructions:
#   run from hw_expts/ directory
#   ENABLE SCRIPTING IN YOUR SALEAE GUI
#   Open Saleae in another window, also at this point you need to run it with
#   the --override flag:
#   Logic --override
# Tips:
#   If you accidentally press the space bar when the triggering window pops up,
#   it kills the trigger wait
import numpy as np
import pandas as pd
import saleae as sal
import os
import sys
import serial
import time
import glob
import re
import platform
import cmd_maker as cmds
import pickle

# Arrays
expt_ids = [3,4,6,7,8,9,10,11,12,27,28,30,31,32,33,34,35,36]
#expt_ids = [7,8,9,10,11,12,27,28,30,31,32,33,34,35,36]
#expt_ids = [3] # 37, 38, 39] # APDS, BLE, ML
#expt_ids = [9] # 37, 38, 39] # APDS, BLE, ML
vmin_levels = [1] # Correspond to 1.6



# Scalar macros
# Actual repeats + 1 (for all but catnap)
REPEATS = 6

FORCE_EXPORT = False

DO_EXPORT = REPEATS > 2 or FORCE_EXPORT
#DO_EXPORT = False

RUN_REAL = 1

raw_vhigh = 2.6
vrange = 3.3
Voff = 1.6
real_vsafes = {}

def adc_encode(num):
  return num*4096/vrange

def adc_decode(adc):
  return adc*vrange/4096

VHIGH = np.ceil(raw_vhigh*4096/vrange)

AVG_VSTART = 0

def calc_new_delta(delta,cur_dir,last_dir,cur_min):
  delta = np.abs(delta)
  if last_dir != cur_dir:
    delta = np.floor(delta*.5)
  if cur_min > Voff:
    print("above voff!")
    delta *= -1
  return delta


if RUN_REAL:
  def get_vcap_min(filename):
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals = df.values
    vals = vals[vals[:,0] > 0]
    AVG_VSTART = np.average(vals[0:100,1])
    print("AVG_VSTART ",AVG_VSTART)
    return [min(vals[:,1]),AVG_VSTART] # vcap lives in column 1
else:
  vmin_vals = [1.72, 1.61, 1.605,1.601]
  def get_vcap_min(filename):
    AVG_VSTART = 0
    get_vcap_min.counter = vars(get_vcap_min).setdefault('counter',-1)
    get_vcap_min.counter += 1
    if get_vcap_min.counter < len(vmin_vals):
      return [vmin_vals[get_vcap_min.counter], 1.9]
    else:
      return [1.6, 1.9]


def saleae_capture(host='localhost', port=10429, \
output_dir='/media/abstract/frick/culpeo_results/seiko_expts/', output='outputs', ID='1234', \
capture_time=1,analogRate=125e3,trigger=7, do_export=True):
    s = sal.Saleae(host,port)
    try:
        s.close_all_tabs()
    except:
        print("Could not close tabs")
    time.sleep(2)
    print("connected")
    if s.get_active_device().type == 'LOGIC_4_DEVICE':
            print("Logic 4 does not support setting active channels; skipping")
    else:
            digital = [3,5,6,7]
            analog = [0,1,2,4]
            print("Setting active channels (digital={}, \
                    analog={})".format(digital, analog))
            s.set_active_channels(digital, analog)
            print("Setting trigger channels\n")

    digital, analog = s.get_active_channels()
    print("Reading back active channels:")
    print("\tdigital={}\n\tanalog={}".format(digital, analog))

    rate = s.set_sample_rate_by_minimum(8e6,analogRate)
    print("\tSet to", rate)
    print("Setting collection time to:")
    s.set_capture_seconds(capture_time)
    # Try to set up trigger on done discharging
    s.set_trigger_one_channel(trigger,sal.Trigger.Posedge)

    # Make system directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    path = os.path.abspath(os.path.join(output_dir,output +"_" + ID +".csv"))
    print(path)

    print("Built path!\n")
    # Start the capture
    s.capture_start()
    cap_count = 0
    while not s.is_processing_complete():
        #print("capturing")
        time.sleep(capture_time)
        cap_count = cap_count + capture_time
        if cap_count > 300:
            s.capture_stop()
            print("Error getting data!")
            return -1
    print("Capture complete")
    # Note: changed display_base from separate to dec because we can use it for both analog
    # and digital output. If we need another digital channel we can always do
    # some digging and figure out how to allow digital and analog to have
    # different display bases.
    if do_export:
      s.export_data2(path,digital_channels=[3,5,6,7],analog_channels=[0,1,2,4],time_span=None,format='csv',display_base='dec')
      print("Done capture and writing")
    s.close_all_tabs()
    return 0

# Must be run from hw_expts directory!!
def run_brute_force_tests(vstarts):
  # cd and clean, we assume you run this from the directory where all the files
  # live
  print(vstarts)
  env = cmds.make_cmd(".","."," ")
  full_cmd = env.cd_cmd() + env.clean_cmd()
  print(full_cmd)
  os.system(full_cmd)
  for Vmin in vmin_levels:
    for expt_id in expt_ids:
      vstart_level = vstarts[expt_id].pop()
      delta = 200
      cur_dir = 0
      last_dir = 0
      good_count = 0
      while True:
        # Set output file name
        cur_test_str = "EXT_temp"
        # program ctrl mcu
        vsafe_str = "VSAFE_ID" + str(expt_id) + "=" + str(vstart_level)
        env.flags = cmds.gen_flags("USE_VSAFE=",str(1),"REPEATS=",str(REPEATS),\
        "CONFIG=",str(Vmin),"VSAFE_ID_ARG=",vsafe_str,"EXPT_ID=",str(expt_id),"VHIGH=",str(VHIGH))
        full_cmd = env.clean_cmd() + env.bld_all_cmd() + env.prog_cmd()
        print("Full command is: ", full_cmd)
        if RUN_REAL:
          os.system(full_cmd)
        output_dir = '/media/abstract/frick/culpeo_results/seiko_expts/brute_force/temp/'
        print("Testing  # ",expt_id," vsafe: ",vstart_level)
        # Start saleae, add time to name
        if RUN_REAL:
          result = saleae_capture(output_dir=output_dir, output=cur_test_str,
          ID="00",capture_time=3, trigger=6,do_export=DO_EXPORT)
        else:
          result = 1
        # repeat
        if result == -1:
          continue
        filename = output_dir + cur_test_str + "_00.csv"
        new_min,AVG_VSTART = get_vcap_min(filename)
        print("Avgs start =",AVG_VSTART)
        # if done condition
        print("Min is : ",new_min)
        if ((new_min < Voff  + .0045) and (new_min > Voff - .0045)):
          print("Good count up!")
          real_vsafes['expt_id'] = expt_id
          real_vsafes['vsafe'] = adc_decode(vstart_level)
          real_vsafes['vstart'] = AVG_VSTART
          real_vsafes['vmin'] = new_min
          break
          #if good_count > 1:
          #  real_vsafes['expt_id'] = expt_id
          #  real_vsafes['vsafe'] = adc_decode(vstart_level)
          #  real_vsafes['vstart'] = AVG_VSTART
          #  real_vsafes['vmin'] = new_min
          #  break
          #else:
          #  good_count = good_count + 1
        else:
          good_count = 0
          # set cur dir
          if new_min < Voff:
            cur_dir = 1
          else:
            cur_dir = -1
          delta = calc_new_delta(delta,cur_dir,last_dir,new_min)
          vstart_level = vstart_level + delta
          print("Delta is : ",delta, "vstart level is: ",vstart_level)
          last_dir = cur_dir
      # Print out for each expt
      time_str = time.strftime('%m-%d--%H-%M-%S')
      results_file = open('vsafes_true_' +  str(expt_id) + "_"+ time_str + ".pkl", 'wb')
      pickle.dump(real_vsafes,results_file)
      results_file.close()




if __name__ == "__main__":
  open_culpeo_vsafe= open('../plotting_scripts/culpeo_vsafe.pkl','rb')
  vstarts = pickle.load(open_culpeo_vsafe)
  open_culpeo_vsafe.close()
  run_brute_force_tests(vstarts)
