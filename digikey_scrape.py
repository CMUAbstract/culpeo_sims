import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

MIN_VOLTAGE = 1.8

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

def PlotAgainstESR(esr,var,var_name, var_unit):
  fig, ax = plt.subplots()
  ax.scatter(esr,var)
  ax.set_ylabel(var_name + " (" + var_unit + ")")
  ax.set_xlabel('ESR ($\Omega$)')
  ax.set_title('ESR vs ' + var_name)
  plt.savefig(var_name + "vs_esr.pdf")

def CleanScientificUnit(item,unit):
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
  df['Energy'] = .5*(df['Voltage - Rated']**2 - MIN_VOLTAGE**2)*df['Capacitance']
  # Translate dimensions into area
  df['Size / Dimension'] = df['Size / Dimension'].apply(CleanArea)
  # Derive volume from area and height
  df['Volume'] = df['Size / Dimension']*df['Height - Seated (Max)']
  # Calculate energy density
  df['Energy Density'] = df['Energy']/df['Volume']
  # Next restriction-- Drop caps larger than the Kemet on Arty-----------------
  df =df[df['Volume'] < 27023] # Only look at caps smaller than the kemet
  # ---------------------------------------------------------------------------
  df['Operating Temperature'] = df['Operating Temperature'].apply(CleanTempRange)
  # Plotting!
  ESRs = df['ESR (Equivalent Series Resistance)']
  # ESR vs Cap
  fig,ax = plt.subplots()
  ax.scatter(ESRs,df['Capacitance'])
  ax.set_ylabel('Capacitance (F)')
  ax.set_xlabel('ESR ($\Omega$)')
  ax.set_title('ESR vs Capacitance: COTS supercaps < 10F')
  greater = df[df['ESR (Equivalent Series Resistance)'] > .6]['ESR (Equivalent Series Resistance)'].size
  total = df['ESR (Equivalent Series Resistance)'].size
  percent = 100*greater/total
  ax.text(50,7.5,"{:.2f}".format(percent)+'% > 600 $m\Omega$')
  plt.savefig('cap_vs_esr.pdf')
  #plt.show()
  # ESR vs Price
  PlotAgainstESR(ESRs, df['Price'],"Price","$")
  PlotAgainstESR(ESRs, df['Voltage - Rated'],"Voltage", "V")
  PlotAgainstESR(ESRs, df['Volume'],"Voltage", "mm^3")
  PlotAgainstESR(ESRs, df['Energy'],"Energy", "J")
  PlotAgainstESR(ESRs, df['Energy Density'],"Energy Density", "J/mm^3")
  PlotAgainstESR(ESRs, df['Operating Temperature'], "Temperature Range",\
    "$ ^{\circ}C$")
  plt.show()
