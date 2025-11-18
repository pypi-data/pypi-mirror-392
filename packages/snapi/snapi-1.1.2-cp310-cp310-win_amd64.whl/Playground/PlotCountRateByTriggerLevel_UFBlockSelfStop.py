import sys
import os
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snAPI.Main import *
import matplotlib
import matplotlib.pyplot as plt
import threading
matplotlib.use('TkAgg',force=True)
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    to = time.time()
    sn = snAPI()
    savePTU = False

    sn.getDevice()
    sn.initDevice(MeasMode.T3)
    size = 1048576 * 10
    
    t = 0.1 # in seconds
    numChans = sn.deviceConfig["NumChans"] + 1
    x, sync = [],[]
    chan = [[] for _ in range(numChans)] 
    plt.show(block=False)
    
    for trigLvl in range(-50, 21):
        cnts  = [0] * numChans
        sn.device.setInputEdgeTrig(-1, trigLvl, 1)
        sn.device.setSyncEdgeTrig(trigLvl, 1)
        
        to2 =  time.time()
        if savePTU:
            sn.setPTUFilePath(r"e:\data\PicoQuant\trglvl\trgLvl_" + str(trigLvl) + r".ptu")
        
        sn.unfold.startBlock(100000, size, savePTU)
        
        threading.Timer(1, sn.unfold.stop).start()
        
        while not sn.unfold.isFinished() or sn.unfold.numRead() != 0:
            times, channels = sn.unfold.getBlock()

            for i in range(sn.unfold.numRead()):
                if not sn.unfold.IsMarker(channels[i]):
                    chanIdx = sn.unfold.Channel(channels[i])
                    if chanIdx >= 0:
                        cnts[chanIdx] += 1
        
        for i in range(numChans):
            chan[i].append(cnts[i])
            
        sn.logPrint(trigLvl, cnts)
        x.append(trigLvl)

        if trigLvl % 1 == 0:
            plt.clf()
            for i in range(numChans):
                plt.plot(x, chan[i], linewidth=2.0, label=f"chan{str(i)}")

            plt.xlabel('Trigger Level [mV]')
            plt.ylabel('Counts')
            plt.legend()
            plt.title("Counts / Trigger Level")
            plt.pause(0.2)

    print(time.time()-to)
    plt.show(block=True)  