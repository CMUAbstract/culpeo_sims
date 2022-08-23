import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

MIN_VOLTAGE = 1.2
#MAX_VOLUME = 1570 # CR2032 sized cap
#MAX_VOLUME = 27023 # Size of Arty cap
MAX_VOLUME = 2702300 # no limit
CR2032 = 1570 # 20mm diameter, 5mm height
D_CELL = 52574 # 33mm diameter, 61.5mm height
MOUSE_HAT = 900  # 4mmx15mmx15mm square

RICE = 5
AAA = 3894
GOLF = 40684
PINT = 473176
PENNY = 349
RICE = 22

#MAX_VOLUME = D_CELL
FS= 28
boldness = 300
MS = 24
volumes = [D_CELL, CR2032, MOUSE_HAT]
CAP_LIM = 45e-3
SET_VOLTAGE = 3.3

limit_volume = 0
#MAX_VOLTAGE = 5.5
MAX_VOLTAGE = 400
colors = ['r','g','b','c']
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
    elif re.search('u',new_item):
      pos2 = re.search('\s*u',new_item).start()
      new_item = new_item[:pos2] + "e-6"
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

def PlotSemilog(yvar, esr, var_name, var_unit,ax=None,color='r',label='Test'):
  if ax == None:
    fig, ax = plt.subplots()
  #ax.loglog(esr,yvar,'.',color=color,label =label,markersize=MS)
  #ax.set_ylabel(var_name + " (" + var_unit + ")",fontsize=FS,fontweight=boldness)
  #ax.set_xlabel('ESR ($\Omega$)',fontsize=FS,fontweight=boldness)
  ax.loglog(yvar,esr,'.',color=color,label =label,markersize=MS)
  ax.set_xlabel(var_name + " (" + var_unit + ")",fontsize=FS,fontweight=boldness)
  ax.set_ylabel('ESR ($\Omega$)',fontsize=FS,fontweight=boldness)
  ax.set_xlim([9,10e6])
  #ax.set_title('ESR vs ' + var_name)
  #plt.savefig(var_name + "_vs_esr_semilog.pdf")
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
  ax.legend(fontsize=FS,fontweight=boldness)
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


def CleanDfs(df):
  # Drop caps without listed ESR
  if 'ESR (Equivalent Series Resistance)' in df.columns:
    print("Got it!")
  else:
    df['ESR (Equivalent Series Resistance)'] = '.01'
  df = df[df['ESR (Equivalent Series Resistance)'] != '-']
  df['Test'] = 133
  # Drop caps > $100... that's kinda crazy
  df = df[df['Price'] < 500]
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
  #print(df.loc[df['Voltage - Rated'] > MAX_VOLTAGE])
  print(df['Voltage - Rated'])
  df['Energy'] = .5*(df['Voltage - Rated']**2 - MIN_VOLTAGE**2)*df['Capacitance']
  # Translate dimensions into area
  df['Size / Dimension'] = df['Size / Dimension'].apply(CleanArea)
  # Derive volume from area and height
  df['Volume'] = df['Size / Dimension']*df['Height - Seated (Max)']
  # Calculate energy density
  df['Energy Density'] = df['Energy']/df['Volume']
  # Next restriction-- Drop caps larger than the Kemet on Arty and > 6V -----
  df = df[df['Height - Seated (Max)'] < 10000]
  #df =df[df['Volume'] < 27023] # Only look at caps smaller than the kemet
  df =df[df['Volume'] < MAX_VOLUME] # Only look at caps smaller than a CR2032
  #df = df[df['Voltage - Rated'] < 6]
  df = df[df['Capacitance'] < CAP_LIM] # New
  # ---------------------------------------------------------------------------
  df['Operating Temperature'] = df['Operating Temperature'].apply(CleanTempRange)
  return df


def AddCapLimit(df):
  num_caps = np.floor(CAP_LIM/df['Capacitance'])
  print("num caps are:",num_caps)
  df['Combined Energy'] =  .5*(SET_VOLTAGE**2 - MIN_VOLTAGE**2)*\
    df['Capacitance']*num_caps
  df['Combined Volume'] = df['Volume']*num_caps
  df['Combined ESR'] = df['ESR (Equivalent Series Resistance)']/num_caps
  return df

if __name__ == "__main__":
  df3 = pd.read_csv('digikey_supercapacitors.csv')
  df2 = pd.read_csv('tantalum_capacitors.csv')
  #df = pd.read_csv('highest_capacity_ceramic_capacitors.csv')
  df1 = pd.read_csv('smallest_ceramics.csv')
  df0 = pd.read_csv('aluminum_electrolytic_capacitors.csv')
  dfs = [df0,df1,df2,df3]
  labels = ['Electrolytic','Ceramic','Tantalum','Supercapacitors']
  for count,df in enumerate(dfs):
    dfs[count] = CleanDfs(df)
  # Restrictions:
  # ---------------------------------------------------------------------------
  # Plotting!
  #ESRs = df['ESR (Equivalent Series Resistance)']
  # ESR vs Cap
  #ax = PlotAgainstESR(ESRs,df['Capacitance'], "Capacitance", "F") 
  #greater = df[df['ESR (Equivalent Series Resistance)'] > .6]['ESR (Equivalent Series Resistance)'].size
  #total = df['ESR (Equivalent Series Resistance)'].size
  #percent = 100*greater/total
  #ax.text(10,.4,"{:.2f}".format(percent)+'% > 600 $m\Omega$')
  #plt.savefig('Capacitance_vs_esr.png')

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
  if limit_volume:
    df  = df0
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
  else: # Limit cap 
    fig, ax = plt.subplots()
    for count, df in enumerate(dfs):
      if 'Test' in df.columns:
        print("Updating!")
      dfs[count] = AddCapLimit(df)
      print(dfs[count].nsmallest(3,'Combined Volume'))
      PlotSemilog(df['Combined Volume'],df['Combined ESR'], "Volume",
      "$mm^3$",ax,colors[count],labels[count])
    LabelX = 1e-6
    ax.tick_params(axis='x',labelsize=FS)
    ax.tick_params(axis='y',labelsize=FS)
    ax.axvline(PINT,color='k',lw=2,ls='--')
    ax.text(PINT, LabelX, 'Pint Glass',fontsize=FS,rotation=-90,ha='left')
    ax.axvline(GOLF,color='k',lw=2,ls='--')
    ax.text(GOLF,LabelX,  'Golf Ball',fontsize=FS,rotation=-90,ha='left')
    ax.axvline(AAA,color='k',lw=2,ls='--')
    ax.text(AAA,LabelX*4,  'AAA',fontsize=FS,rotation=-90,ha='left')
    ax.axvline(PENNY,color='k',lw=2,ls='--')
    ax.text(PENNY,LabelX,  'US Penny',fontsize=FS,rotation=-90,ha='left')
    ax.axvline(RICE,color='k',lw=2,ls='--')
    ax.text( RICE,LabelX/2, 'Rice Grain',fontsize=FS,rotation=-90,ha='left')
    ax.legend(fontsize=FS,framealpha=1)

    ax.annotate("RA Cap1",xy=(158802,10e-3), xytext=(2e4,1e-1), fontsize=FS,
    arrowprops=dict(arrowstyle="-", color='k',lw=1))
    ax.annotate("RA Cap2",xy=(3776949,2.6e-3), xytext=(2e6,1e-5), fontsize=FS,
    arrowprops=dict(arrowstyle="-", color='k',lw=1))
    ax.annotate("This Work:\n6 parts\n20nA DCL",xy=(43.2, 4.16),
    xytext=(43.2,3e-2), color='c',fontsize=FS, arrowprops=dict(arrowstyle="-",
    color='c',lw=2))
    # More arrows!
    smallest_ceramic =  (572,5e-6)
    smallest_tantalum = (459,0.0245)
    ax.annotate("2,045\nparts",xy=smallest_ceramic,
    xytext=(1e3,5e-5), fontsize=FS, color='g',arrowprops=dict(arrowstyle="-",
    color='g',lw=2))
    ax.annotate("26mA\nDCL",xy=smallest_tantalum,
    xytext=(1e2,1e-3), fontsize=FS,color='b',arrowprops=dict(arrowstyle="-",
    color='b',lw=2))
    plt.savefig("Vol_vs_esr_loglog.pdf",format='pdf',bbox_inches='tight')
    #PlotAgainstESR(df['Combined ESR'], df['Combined Volume'], "Runs in : " +
    #str(CAP_LIM) + " F", "Volume")
    #print(df.nsmallest(3,'Combined Volume'))
  plt.show()
  #print("Volume vs Capacitance correlation:",np.corrcoef(df['Capacitance'],df['Volume'])[0,1])
  #print("Correlation with Temperature is: ",np.corrcoef(ESRs,\
  #df['Operating Temperature'])[0,1])
  #print("Correlation with Volume is: ",np.corrcoef(ESRs,df['Volume'])[0,1])
  #print("Correlation with Capacitance is: ",np.corrcoef(ESRs,df['Capacitance'])[0,1])
  #print("Correlation with Energy Density is: ",np.corrcoef(ESRs,df['Energy Density'])[0,1])
  #print("Correlation with Price is: ",np.corrcoef(ESRs,df['Price'])[0,1])
  #PlotMultivariate(ESRs,df['Price'], "Price",df['Capacitance'],"Capacitance","F")
  #PlotMultivariate(ESRs,df['Capacitance'],"Capacitance",df['Price'], "Price","$")
  #plt.show()
# Best:
# F980G227MSA (220uF) -- 26mA of leakage
# 04024D226MAT2A (22uF) 0.21*2045 = total cost $430
# 10TPV1000M8X10.5
