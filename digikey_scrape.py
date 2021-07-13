import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

MIN_VOLTAGE = 1.2
#MAX_VOLUME = 1570 # CR2032 sized cap
#MAX_VOLUME = 27023 # Size of Arty cap
CR2032 = 1570 # 20mm diameter, 5mm height
D_CELL = 52574 # 33mm diameter, 61.5mm height
MOUSE_HAT = 900  # 4mmx15mmx15mm square

volumes = [D_CELL, CR2032, MOUSE_HAT]

MAX_VOLUME = D_CELL
MAX_VOLTAGE = 5.5

good_markers = [".","v",">","*","x","+","d","<","^","p"]
def CleanTempRange(temps):
  temp_range = re.findall(r'[0-9-]+',temps)
  start = float(temp_range[0])
  stop = float(temp_range[1])
  return stop - start

def CleanHeight(height):
  # Drop anything before the (xx.xxmm)
  if re.search('mm',height):
    pos = re.search('mm',height).start()
    new_height = height[:pos]
    if re.search('\(',new_height):
      pos2 = re.search('\(',new_height).start()
      new_height = new_height[pos2+1:]
    return float(new_height)

def CleanArea(dims):
  if re.search('Dia \(',dims):
    pos = re.search('Dia \(',dims).end()
    diameter = dims[pos:]
    pos2 = re.search('mm\)', diameter).start()
    diameter = diameter[:pos2]
    d = float(diameter)
    return np.pi*(d/2)**2
  elif re.search('L.*W \(',dims):
    pos = re.search('L.*W \(',dims).end()
    dims = re.findall(r'[0-9.]+',dims[pos:])
    length = dims[0]
    width = dims[1]
    return float(length) * float(width)

def CleanScientificUnit(item, unit):
  # Scrub out the F, if there's a m change it to e-3
  if re.search(unit,item):
    pos = re.search(unit,item).start()
    new_item = item[:pos]
    if re.search('m',new_item):
      pos2 = re.search('\s*m',new_item).start()
      new_item = new_item[:pos2] + "e-3"
    return float(new_item)
  else:
    return float(item)

def PlotAgainstESR(esr, var, var_name, var_unit):
  fig, ax = plt.subplots()
  ax.scatter(esr,var)
  ax.set_ylabel(var_name + " (" + var_unit + ")")
  ax.set_xlabel('ESR ($\Omega$)')
  ax.set_title('ESR vs ' + var_name)
  ax.axvline(.6,color='k',lw=2,ls='--')
  plt.savefig(var_name + "_vs_esr.png")
  return ax

def PlotMultivariate(x, group_by, group_name, var, var_name, var_unit):
  fig, ax = plt.subplots()
  upper = max(group_by)
  lower = min(group_by)
  group_lower = lower
  count = 0
  for group_upper in np.arange(lower,upper,(upper-lower)/10):
    x_vals = x[(group_by > group_lower) & (group_by < group_upper)]
    y_vals = var[(group_by > group_lower) & (group_by < group_upper)]
    group_label = "[" + str(group_lower) + "--" + str(group_upper) + "]"
    ax.scatter(x_vals,y_vals,label=group_label,marker=good_markers[count])
    group_lower = group_upper
    count += 1
  ax.set_ylabel(var_name + " (" + var_unit + ")")
  ax.set_xlabel('ESR ($\Omega$)')
  ax.set_title('ESR vs ' + var_name + " Grouped by " + group_name)
  ax.legend()
  plt.savefig(var_name + "_vs_esr_multi_.png")

def PlotCorrelation(xs, group_by, group_name, var, var_name):
  uniques = group_by.unique()
  corrs = []
  groups = []
  for cap in uniques:
    if (len(df[group_by == cap]) < 3):
      continue
    groups.append(cap)
    x = xs[group_by == cap]
    y = var[group_by == cap]
    corrs.append(np.corrcoef(x,y)[0,1])
    print(group_name + " = "+ str(cap) + " Corr with " + var_name  + " is: ",np.corrcoef(x,y)[0,1])
  fig, ax = plt.subplots()
  ax.scatter(groups,corrs)
  ax.set_title('Correlation between ESR and ' + var_name + ' for fixed ' +\
  group_name)


if __name__ == "__main__":
  df = pd.read_csv('digikey_supercapacitors.csv')
  # Restrictions:
  # ---------------------------------------------------------------------------
  # Drop caps without listed ESR
  df = df[df['ESR (Equivalent Series Resistance)'] != '-']
  # Drop caps > $100... that's kinda crazy
  df = df[df['Price'] < 100]
  # ---------------------------------------------------------------------------
  # Clean up capacitance
  df['Capacitance'] = df['Capacitance'].apply(CleanScientificUnit,args='F')
  # Clean up ESR
  df['ESR (Equivalent Series Resistance)'] = \
  df['ESR (Equivalent Series Resistance)'].apply(CleanScientificUnit,args=['Ohm'])
  # Restriction ------drop caps with ESR > 100, that's just crazy -------------
  df = df[df['ESR (Equivalent Series Resistance)'] < 100]
  # ---------------------------------------------------------------------------
  # Clean height
  df['Height - Seated (Max)'] = df['Height - Seated (Max)'].apply(CleanHeight)
  # Clean Voltage
  df['Voltage - Rated'] = df['Voltage - Rated'].apply(CleanScientificUnit,args='V')
  # Calculate Energy
  print(MAX_VOLTAGE)
  df.loc[df['Voltage - Rated'] > MAX_VOLTAGE, 'Voltage - Rated'] = MAX_VOLTAGE
  print(df.loc[df['Voltage - Rated'] > MAX_VOLTAGE])
  print(df['Voltage - Rated'])
  df['Energy'] = .5*(df['Voltage - Rated']**2 - MIN_VOLTAGE**2)*df['Capacitance']
  # Translate dimensions into area
  df['Size / Dimension'] = df['Size / Dimension'].apply(CleanArea)
  # Derive volume from area and height
  df['Volume'] = df['Size / Dimension']*df['Height - Seated (Max)']
  # Calculate energy density
  df['Energy Density'] = df['Energy']/df['Volume']
  # Next restriction-- Drop caps larger than the Kemet on Arty and > 6V -----
  df = df[df['Height - Seated (Max)'] < 10]
  #df =df[df['Volume'] < 27023] # Only look at caps smaller than the kemet
  df =df[df['Volume'] < MAX_VOLUME] # Only look at caps smaller than a CR2032
  #df = df[df['Voltage - Rated'] < 6]
  df = df[df['Capacitance'] < 5] # New
  # ---------------------------------------------------------------------------
  df['Operating Temperature'] = df['Operating Temperature'].apply(CleanTempRange)
  # Plotting!
  ESRs = df['ESR (Equivalent Series Resistance)']
  # ESR vs Cap
  ax = PlotAgainstESR(ESRs,df['Capacitance'], "Capacitance", "F") 
  greater = df[df['ESR (Equivalent Series Resistance)'] > .6]['ESR (Equivalent Series Resistance)'].size
  total = df['ESR (Equivalent Series Resistance)'].size
  percent = 100*greater/total
  ax.text(10,.4,"{:.2f}".format(percent)+'% > 600 $m\Omega$')
  plt.savefig('Capacitance_vs_esr.png')
  #PlotAgainstESR(ESRs, df['Price'],"Price","$")
  #PlotAgainstESR(ESRs, df['Voltage - Rated'],"Voltage", "V")
  #PlotAgainstESR(ESRs, df['Volume'],"Volume", "mm^3")
  #PlotAgainstESR(ESRs, df['Energy'],"Energy", "J")
  #PlotAgainstESR(ESRs, df['Energy Density'],"Energy Density", "J/mm^3")
  #PlotAgainstESR(ESRs, df['Operating Temperature'], "Temperature Range",\
  #  "$ ^{\circ}C$")
  #PlotAgainstESR(df['Combined ESR'], df['Combined Energy'], "Total Energy", "J")
  #
  #PlotCorrelation(ESRs,df['Capacitance'], "Capacitance", df['Price'],"Price") 
  #PlotCorrelation(ESRs,df['Capacitance'], "Capacitance", df['Volume'],"Volume") 
  #PlotCorrelation(ESRs,df['Capacitance'], "Capacitance", df['Voltage - Rated'],"Voltage") 
  #PlotCorrelation(ESRs,df['Capacitance'], "Capacitance", df['Energy Density'],\
  #  "Energy Density") 
  #PlotCorrelation(ESRs,df['Volume'], "Volume", df['Energy Density'],\
  #  "Energy Density") 
  for limit in volumes:
    # Calculate max energy within volume restriction
    num_caps = np.floor(limit/df['Volume'])
    df['Combined Energy'] =  .5*(df['Voltage - Rated']**2 - MIN_VOLTAGE**2)*\
      df['Capacitance']*num_caps
    df['MobileNetRuns'] = df['Combined Energy']/5 # 1 MobileNet run on a TPU
    df['Combined ESR'] = df['ESR (Equivalent Series Resistance)']/num_caps
    PlotAgainstESR(df['Combined ESR'], df['MobileNetRuns'], "Runs in volume: " +
    str(limit) + " mm^3", "MobileNet Iterations")
    max_ind = df['MobileNetRuns'].idxmax()
    print("Max for " + str(limit) + " " + str(max_ind))
    print("\tBest volume is: " + str(df['Volume'][max_ind]) + " Part number is "
    + df['Mfr Part #'][max_ind])
  
  plt.show()

  print("Correlation with Temperature is: ",np.corrcoef(ESRs,\
  df['Operating Temperature'])[0,1])
  print("Correlation with Volume is: ",np.corrcoef(ESRs,df['Volume'])[0,1])
  print("Correlation with Capacitance is: ",np.corrcoef(ESRs,df['Capacitance'])[0,1])
  print("Correlation with Energy Density is: ",np.corrcoef(ESRs,df['Energy Density'])[0,1])
  print("Correlation with Price is: ",np.corrcoef(ESRs,df['Price'])[0,1])
  #PlotMultivariate(ESRs,df['Price'], "Price",df['Capacitance'],"Capacitance","F")
  #PlotMultivariate(ESRs,df['Capacitance'],"Capacitance",df['Price'], "Price","$")
  #plt.show()
