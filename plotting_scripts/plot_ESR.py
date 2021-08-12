import matplotlib.patches as patches
import pandas as pd
import numpy as np
import sys
import matplotlib
#matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import re
import glob
import esr_data


T = 10.0
duty_cycles = ['99.999','99.99','99.9','99','90']
loads = ['5','10','25','50']
#caps = [esr_data.BestCapESR,esr_data.kemetESR,esr_data.seikoESR]
caps = [esr_data.seikoESR]
#colors = ["#084594", "#4292c6", "#9ecae1"]
colors = ["#eff3ff","#bdd7e7","#6baed6","#3182bd","#08519c"]
#labels = ['BestCap','Kemet','Seiko']
labels = ['5mA','10mA','25mA','50mA']
def plot_esr():
  fig, ax = plt.subplots()
  esrs = []
  times = []
  scatter_colors =[]
  for cap_count, cap in enumerate(caps):
    for load_count, load in enumerate(loads):
      for duty_cycle in duty_cycles:
        time_on = T - .01*float(duty_cycle)*T
        if duty_cycle in cap.keys():
          if load in cap[duty_cycle].keys():
            esrs.append(float(cap[duty_cycle][load]))
            times.append(time_on)
            scatter_colors.append(colors[load_count])
  plt.scatter(x=times,y=esrs, s=50,c=scatter_colors,alpha=1,edgecolors='k')
  plt.xticks(fontsize=12)
  plt.yticks(fontsize=16)
  ax.set_xscale('log')
  boldness = 300
  # y = A + B log(x)
  logfit = np.polyfit(np.log(times),esrs,2)
  print("Log fit is: ",logfit)
  curve2 = np.poly1d(logfit)
  xp = np.linspace(min(times), max(times), 1000)
  #ax.plot(xp,curve(xp),'r')
  ax.plot(xp,curve2(np.log(xp)),colors[-1])
  plt.grid(True,which="both")
  ax.set_xlabel('Pulse Time (s)', fontsize=16,fontweight=boldness)
  ax.set_ylabel('ESR ($\Omega$)', fontsize=16,fontweight=boldness)
  ratio = 1
  legs = []
  for i,label in enumerate(labels):
    legs.append(patches.Patch(fc=colors[i],lw=1,alpha=1,label=label,ec='k'))
  fig.legend(handles=legs,loc='upper center',
  ncol=len(labels),fontsize=12,bbox_to_anchor=(.5,.75))
  xleft, xright = ax.get_xlim()
  ybottom, ytop = ax.get_ylim()
  ax.set_aspect(abs((xright-xleft)/(ybottom-ytop))*ratio)
  plt.show()
  fig.savefig('esr_plot.pdf',format='pdf',bbox_inches='tight')




if __name__ == "__main__":
  plot_esr()

