import sys
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snAPI.Main import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg',force=True)
print("Switched to:",matplotlib.get_backend())

if(__name__ == "__main__"):

    sn = snAPI()
    sn.getDevice()
    sn.initDevice(MeasMode.T2)
    
    t = 0.1 # in seconds
    numChans = sn.deviceConfig["NumChans"]
    x, sync = [],[]
    chan = [[] for _ in range(numChans)] 
    plt.show(block=False)

    for trigLvl in range(-120, 21):
        cnts  = []
        sn.device.setInputEdgeTrig(-1, trigLvl, 0)
        sn.device.setSyncEdgeTrig(trigLvl, 0)
        
        sn.histogram.setRefChannel(1)
        sn.histogram.measure(round(1000*t))
        data, bins = sn.histogram.getData()
        for i in range(numChans):
            cnts.append(sum(data[i+1]) / t)
            chan[i].append(cnts[i])
            
        print(trigLvl, cnts)
        x.append(trigLvl)
        
        plt.clf()
        for i in range(numChans):
            plt.plot(x, chan[i], linewidth=2.0, label=f"chan{str(i)}")

        plt.xlabel('Trigger Level [mV]')
        plt.ylabel('Counts')
        plt.legend()
        plt.title("Counts / Trigger Level")
        plt.pause(0.01)
    
    plt.show(block=True)