# Script for transferring estimates_*.pkl produced by the
# comparing_online_methods.py into .h files usable by vsafe_test.py
# We'll start by pulling in just the ones for Culpeo-dynamic (where we measure
# the capacitor minimum)

import pandas as pd
import numpy as np
import sys
import re
import glob
import pickle as pkl

ESTIMATES_PATH = "./estimates_1_0.01.pkl"
SECS = .00001
V_RANGE = 3.3
NEW_FILE_NAME="vcap_min_vsafe.h"
EXTRACT_FILE_NAME="hardware_vsafe.pkl"

def make_adc_file_str(expt_id, val):
  adc = np.ceil(4096*val/V_RANGE)
  adc_val = int(adc)
  file_str = "#define VSAFE_ID" + str(expt_id) + " " + str(adc_val) + "\n"
  return file_str

def estimates_extract(filename):
  ests = pkl.load(open(filename,'rb'))
  ests = ests['vcap']
  new_est = {}
  for expt in ests.keys():
    new_est[expt] = np.average(ests[expt][.00001])
    print(expt,":",new_est[expt])
  new_file = open(EXTRACT_FILE_NAME,"wb")
  pkl.dump(new_est,new_file)

if __name__ == "__main__":
  Vsafe_file = open(NEW_FILE_NAME,"w")
  estimates = pkl.load(open(ESTIMATES_PATH,"rb"))
  estimates = estimates["vcap"]
  for expt in estimates.keys():
    print(expt)
    Vsafe = estimates[expt][SECS]
    #print(Vsafe)
    if (np.std(Vsafe) > 0.005):
      print("Error! std dev too big",np.std(Vsafe))
      print(Vsafe)
    Vsafe = np.average(Vsafe)
    Vsafe_str = make_adc_file_str(expt,Vsafe)
    Vsafe_file.write(Vsafe_str)
  Vsafe_file.close() 

