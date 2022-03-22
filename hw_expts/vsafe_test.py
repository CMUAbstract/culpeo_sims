# Script for testing different Vsafes on experiments specified in
# loadProfiling.h
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

# Arrays
#expt_ids = [3,4,6,7,8,9,10,11,12,27,28,30,31,32,33,34,35,36]
expt_ids = [38] # 37, 38, 39] # APDS, BLE, ML
#expt_ids = [9] # 37, 38, 39] # APDS, BLE, ML
vmin_levels = [1] # Correspond to 1.6
#Vstart_names = ["Vsafe_culpeo","Vsafe_conservative","Vsafe_catnap","Vsafe_datasheet"]#"Vsafe_naive","Vsafe_naive_better"]
Vstart_names = ["Vsafe_conservative"]#"Vsafe_catnap","Vsafe_conservative","Vsafe_naive","Vsafe_naive_better"]


expt_lists = {
  "Vsafe_culpeo": [33,38,39],
  "Vsafe_conservative": [1,3,6,7,8,10,11,12,38,39],
  "Vsafe_datasheet": [27,28,33,38],
  "Vsafe_catnap": [6,7,8,9,10,11,12,38,39]
}
#Vstart_names = ["Vsafe_catnap"]#"Vsafe_naive","Vsafe_naive_better"]

# Scalar macros
# Actual repeats + 1 (for all but catnap)
REPEATS = 2

FORCE_EXPORT = False

DO_EXPORT = REPEATS > 2 or FORCE_EXPORT
#DO_EXPORT = False

raw_vhigh = 2.6
vrange = 3.3

VHIGH = np.ceil(raw_vhigh*4096/vrange)

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
            digital = [3,5,6,7] # used to be 3,5,6,7
            analog = [0,1,2,4]# used to be 0,1,2,4
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
def run_vsafe_tests():
  # cd and clean, we assume you run this from the directory where all the files
  # live
  env = cmds.make_cmd(".","."," ")
  full_cmd = env.cd_cmd() + env.clean_cmd()
  print(full_cmd)
  os.system(full_cmd)
  repeats = REPEATS
  for Vstart_name in Vstart_names:
    for Vmin in vmin_levels:
      for expt_id in expt_ids:
        if expt_lists[Vstart_name].count(expt_id) < 1:
          continue
        # Set output file name
        cur_test_str = "EXPT_" + str(expt_id) + "_"+str(Vmin) + "_" + Vstart_name + "_"
        # program ctrl mcu
        env.flags = cmds.gen_flags("USE_VSAFE=",str(1),"REPEATS=",str(repeats),\
        "CONFIG=",str(Vmin),"EXPT_ID=",str(expt_id),"VSAFE_PATH=./",Vstart_name,"VHIGH=",str(VHIGH))
        full_cmd = env.clean_cmd() + env.bld_all_cmd() + env.prog_cmd()
        print(full_cmd)
        os.system(full_cmd)
        if expt_id > 36:
          output_dir = '/media/abstract/frick/culpeo_results/case_study/'
        else:
          output_dir = '/media/abstract/frick/culpeo_results/seiko_expts/'
        for i in range(repeats-1):
          print("Testing  # ",i)
          # Start saleae, add time to name
          time_ID = time.strftime('%m-%d--%H-%M-%S')
          if expt_id == 38 or expt_id == 39:
            result = saleae_capture(output_dir=output_dir, output=cur_test_str,\
            ID=time_ID, capture_time=3, trigger=6,do_export=DO_EXPORT)
          else:
            result = saleae_capture(output_dir=output_dir, output=cur_test_str,
            ID=time_ID,capture_time=3, trigger=6,do_export=DO_EXPORT)
          # repeat
          if result == -1:
            continue




if __name__ == "__main__":
  run_vsafe_tests()
