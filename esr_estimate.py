# Script for feeding in current trace and spitting out a predicted esr

import matplotlib.patches as patches
import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import os
import min_voltage_notes as minV
from scipy.signal import butter,filtfilt
import pickle


R_SHUNT = 4.7
V_RANGE = 3.3
V_MIN = 1.6
CAP_VAL = 45e-3
EFF_VMIN = .5
DO_PLOT = False
datasheet_esr = 25/6

name_map = {"APDS": 37,'BLE':38,'ML':39,'FAST':40}

# Fit polynomial, we currently assume y = A + B log(x) format
#fits = [4.67905365, 32.95741414]
#fits = [4.0223403,  31.35076712]
fits =  [ 0.44363009,  7.63255919, 35.18498227]
curve = np.poly1d(fits)

def make_adc_file_str(expt_id, val):
  adc = np.ceil(4096*val/V_RANGE)
  adc_val = int(adc)
  file_str = "#define VSAFE_ID_" + str(expt_id) + " " + str(adc_val) + "\n"
  return file_str

def make_adc_val(val):
  adc = np.ceil(4096*val/V_RANGE)
  adc_val = int(adc)
  return adc_val


def butter_lowpass_filter(data, cutoff, nyq, order):
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

def extract_esr(I,vals,cutoff=1e3):
  # Smooth out signal
  fs = 1/(vals[1,0]-vals[0,0])
  nyq = fs/2
  filtered_I = butter_lowpass_filter(I,cutoff,nyq,2)
  if DO_PLOT:
    fig, ax = plt.subplots()
    ax.plot(vals[:,0],I,'r.')
    ax.plot(vals[:,0],filtered_I)
    plt.show()
  # Get max I
  max_ind = np.argmax(filtered_I)
  max_I = max(filtered_I)
  print("Max i: ",max_I)
  print("Max ind: ",max_ind)
  # Find base of pulse
  i = max_ind
  #while(filtered_I[i + 1] < filtered_I[i]):
  while((i < len(filtered_I) -1) and filtered_I[i + 1] > max_I/2):
    i += 1
    #print(i)
  pulse_end = i
  print("pulse end: ",vals[pulse_end,0])
  i = max_ind
  #while(filtered_I[i - 1] < filtered_I[i]):
  while(i > 0 and filtered_I[i - 1] > max_I/2):
    i -= 1
    #print(i)
  pulse_start = i
  print("pulse start: ",vals[pulse_start,0])
  # Use that as your pulse time
  pulse_time = vals[pulse_end,0] - vals[pulse_start,0]
  print("Pulse time is: ",pulse_time)
  # Pass through polyfit
  y = curve(np.log(pulse_time))
  if y < 0:
    print("ESR is negative and we're screwed")
    print(esr)
    sys.exit(1)
  # Return expected ESR
  return y


def append_to_dict(sys,app,vsafe):
  filename = sys +"_multi_vsafes_" + str(V_MIN) + ".pkl"
  if os.path.exists(filename):
    fr = open(filename,"rb")
    mv = pickle.load(fr)
    fr.close()
  else:
    mv = {}
  fw = open(filename,"wb")
  mv[name_map[app]] = vsafe
  pickle.dump(mv,fw)
  fw.close()

def calc_vsafes(I,V,dt,esr,name):
  name = name.upper()
  # Catnap
  start_avg = np.average(V[0:100])
  stop_avg = np.average(V[-100:])
  print("Start: ",start_avg," Stop: ",stop_avg)
  catnap_E = .5*CAP_VAL*(start_avg**2 - stop_avg**2)
  catnap_Vsafe = np.sqrt(2*catnap_E/CAP_VAL + V_MIN**2)
  print("Catnap vsafe: ", catnap_Vsafe)
  catnap_file_str = make_adc_file_str(name,catnap_Vsafe)
  catnap_vsafe = open("catnap_"+name+"_"+str(V_MIN),"w")
  catnap_vsafe.write(catnap_file_str)
  catnap_vsafe.close()
  append_to_dict("catnap",name,catnap_Vsafe)
  
  # Point estimate
  n = EFF_VMIN
  max_i = np.amax(I)*2.56/(n*V_MIN)
  conservative_Vsafe = np.sqrt(2*catnap_E/CAP_VAL + (V_MIN + max_i*minV.CAP_ESR)**2)
  print("Conservative vsafe: ", conservative_Vsafe)
  conservative_file_str = make_adc_file_str(name,conservative_Vsafe)
  cons_vsafe = open("conservative_"+name+"_"+str(V_MIN),"w")
  cons_vsafe.write(conservative_file_str)
  cons_vsafe.close()
  append_to_dict("conservative",name,conservative_Vsafe)
  # Culpeo
  minV.CAP_ESR = esr
  minV.MIN_VOLTAGE = V_MIN
  Vsafe = minV.calc_min_forward(I,dt,DO_PLOT)
  print("Culpeo vsafe: ", Vsafe)
  culpeo_file_str = make_adc_file_str(name,Vsafe)
  culpeo_vsafe = open("culpeo_"+name+"_"+str(V_MIN),"w")
  culpeo_vsafe.write(culpeo_file_str)
  culpeo_vsafe.close()
  append_to_dict("culpeo",name,Vsafe)
  # Datasheet
  minV.CAP_ESR = datasheet_esr
  datasheet_Vsafe = minV.calc_min_forward(I,dt,DO_PLOT)
  print("Datasheet vsafe: ", datasheet_Vsafe)
  datasheet_file_str = make_adc_file_str(name,datasheet_Vsafe)
  datasheet_vsafe = open("datasheet_"+name+"_"+str(V_MIN),"w")
  datasheet_vsafe.write(datasheet_file_str)
  datasheet_vsafe.close()
  append_to_dict("datasheet",name,datasheet_Vsafe)

if __name__ == "__main__":
  if (len(sys.argv) < 2):
    print("Error! need to pass in file")
    sys.exit(1)
  filename = sys.argv[1]
  try:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  except:
    df = pd.read_csv(filename, mangle_dupe_cols=True,
         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  vals = df.values
  # Prune filename
  print(filename)
  pos = re.search('/',filename).end()
  print(pos)
  filename = filename[pos:]
  app_name =  re.findall(r'[a-z]+',filename)[0]
  print(app_name)
  if app_name == 'apds':
    #vals = vals[vals[:,0] < .56]
    vals = vals[vals[:,0] < .557063]
    vals = vals[vals[:,0] > .5144]
    cutoff = 2e3
  elif  app_name == 'ml':
    cutoff = 5e1
    vals = vals[vals[:,0] < 1.101263]
    #vals = vals[vals[:,0] < 1.103]
    vals = vals[vals[:,0] > .0026]
  elif app_name == 'ble':
    cutoff = 5e2
    vals = vals[vals[:,0] < 1.41717608]
    #vals = vals[vals[:,0] < 1.002]
    vals = vals[vals[:,0] > .417]
  elif app_name == 'fast':
    cutoff = 5e1
    vals = vals[vals[:,0] < .126]
    vals = vals[vals[:,0] > .0026]
  else:
    print("App name not found:",app_name)
    sys.exit(1)

  diffs = np.subtract(vals[:,3],vals[:,2])
  numbers = re.findall(r'[0-9]+',filename)
  gain = int(numbers[-1])
  print(gain)
  I = np.divide(diffs,R_SHUNT*gain)
  esr = extract_esr(I,vals,cutoff)
  print("use esr: ",esr)
  dt = vals[1,0] - vals[0,0]
  if app_name == 'apds' or app_name == 'fast':
    # Need second file
    filename = sys.argv[2]
    try:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True)#skiprows=[0])
    except:
      df = pd.read_csv(filename, mangle_dupe_cols=True,
           dtype=np.float64, skipinitialspace=True,skiprows=[0])
    vals_V = df.values
    if app_name == 'apds':
      vals_V = vals_V[vals_V[:,0] < .557063]
      #vals_V = vals_V[vals_V[:,0] < .56]
      # We scoot this a little further away so we don't artifically get the up
      # swing after releasing the cap... despite the fact that Catnap would end up
      # seeing that
      vals_V = vals_V[vals_V[:,0] > .5144]
      V = vals_V[:,1]
      times = vals_V[:,0]
    if app_name == 'fast':
      #vals_V = vals_V[vals_V[:,0] < .138]
      vals_V = vals_V[vals_V[:,0] < .135763]
      # We scoot this a little further away so we don't artifically get the up
      # swing after releasing the cap... despite the fact that Catnap would end up
      # seeing that
      vals_V = vals_V[vals_V[:,0] > .026]
      V = vals_V[:,1]
      times = vals_V[:,0]

  #elif app_name == 'fast': #TODO this needs its own cap trace
  #  filename = sys.argv[2]
  #  try:
  #    df = pd.read_csv(filename, mangle_dupe_cols=True,
  #         dtype=np.float64, skipinitialspace=True)#skiprows=[0])
  #  except:
  #    df = pd.read_csv(filename, mangle_dupe_cols=True,
  #         dtype=np.float64, skipinitialspace=True,skiprows=[0])
  #  vals_V = df.values
  #  vals_V = vals_V[vals_V[:,0] > .45]
  #  V = vals_V[:,1]
  #  times = vals_V[:,0]
  else:
    V = vals[:,1]
    times = vals[:,0]
  if DO_PLOT:
    fig, ax = plt.subplots()
    ax.plot(times,V)
    plt.show()
  calc_vsafes(I,V,dt,esr,app_name)
  sys.exit(0)
  filtered_I = butter_lowpass_filter(I,1e2,(1/dt)*.5,2)
  fig, ax = plt.subplots()
  ax.plot(I,'r.')
  ax.plot(filtered_I)
  plt.show() 
  X = np.fft.rfft(filtered_I)
  X_mag = np.abs(X)
  #X_mag = np.square(X_mag)
  N = len(filtered_I)
  freq_step = 1/(vals[1,0] - vals[0,0])
  freqs = np.linspace(0,(N-1)*freq_step,N)
  freqs_plt = freqs[0:int(N/2+1)]
  X_mag_plt = 2*X_mag[0:int(N/2+1)]
  X_mag_plt[0] = X_mag[0]
  fig, ax = plt.subplots()
  ax.plot(freqs_plt,X_mag_plt)
  plt.show()
  print("Used esr: ",esr)
  calc_vsafes(filtered_I,V,dt,esr,app_name)


