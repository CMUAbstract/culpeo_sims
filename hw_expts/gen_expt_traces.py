# Script for running the different experiments that we'll test vsafe with
# Software setup instructions:
#   run from hw_expts/ directory
#   ENABLE SCRIPTING IN YOUR SALEAE GUI
#   Open Saleae in another window
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
#expt_ids = range(13,37) #range is not inclusive of the stop val
expt_ids = [13]

def saleae_capture(host='localhost', port=10429, \
output_dir='./expt_output_traces/', output='outputs', ID='1234', \
capture_time=1,analogRate=125e3):
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
            digital = [2,5,6,7]
            analog = [0,1,3,4]
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
    s.set_trigger_one_channel(7,sal.Trigger.Posedge)

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
    s.export_data2(path,digital_channels=[2,5,6,7],analog_channels=[0,1,3,4],time_span=None,format='csv',display_base='dec')
    s.close_all_tabs()
    print("Done capture and writing")
    return 0


# Must be run from hw_expts directory!!
def run_expt_baselines():
  # cd and clean, we assume you run this from the directory where all the files
  # live
  env = cmds.make_cmd(".","."," ")
  full_cmd = env.cd_cmd() + env.clean_cmd()
  print(full_cmd)
  os.system(full_cmd)
  for expt_id in expt_ids:
    # program ctrl mcu
    # We toss repeats in just to make sure if we somehow miss it we'll get it
    # next time
    env.flags = cmds.gen_flags("REPEATS=",str(10),\
    "EXPT_ID=",str(expt_id))
    full_cmd = env.clean_cmd() + env.bld_all_cmd() + env.prog_cmd()
    print(full_cmd)
    os.system(full_cmd)
    # Set output file name
    cur_test_str = "expt_" + str(expt_id) + ".csv"
    # Start saleae, add time to name
    result = saleae_capture(output=cur_test_str,capture_time=3)


if __name__ == "__main__":
  run_expt_baselines()

