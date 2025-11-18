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
    sn.initDevice(MeasMode.Histogram, RefSource.Internal)
    x, sync, chan1, chan2, chan3, chan4 = [],[],[],[],[],[]
    plt.show(block=False)
    sn.deviceConfig["TriggerType"] = "CFD"
    
    for zxLvl in range(0, 41, 10):
        for trigLvl in range(0, 500, 10):
            if sn.deviceConfig["TriggerType"] == "Edge":
                sn.device.setInputEdgeTrig(-1, trigLvl, 0)
                sn.device.setSyncEdgeTrig(trigLvl, 0)
            elif sn.deviceConfig["TriggerType"] == "CFD":
                sn.device.setInputCFD(-1, trigLvl, zxLvl)
                sn.device.setSyncCFD(trigLvl, zxLvl)
                
            cntRs = sn.getCountRates()
        
            sn.logPrint(trigLvl, zxLvl, cntRs)
            x.append(trigLvl)
            sync.append(cntRs[0])
            chan1.append(cntRs[1])
            chan2.append(cntRs[2])
            # chan3.append(cntRs[3])
            # chan4.append(cntRs[4])
            
            plt.clf()
            plt.plot(x, sync, linewidth=2.0, label='sync')
            plt.plot(x, chan1, linewidth=2.0, label='chan1')
            plt.plot(x, chan2, linewidth=2.0, label='chan2')
            # plt.plot(x, chan3, linewidth=2.0, label='chan3')
            # plt.plot(x, chan4, linewidth=2.0, label='chan4')
            plt.xlabel('Trigger Level [mV]')
            plt.ylabel('Counts')
            plt.legend()
            plt.title("Counts / Trigger Level")
            plt.pause(0.2)
            
    plt.show(block=True)