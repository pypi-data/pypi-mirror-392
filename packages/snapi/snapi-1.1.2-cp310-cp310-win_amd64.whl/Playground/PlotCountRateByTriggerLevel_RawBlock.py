import sys
import os 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snAPI.Main import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg',force=True)
print("Switched to:",matplotlib.get_backend())
import time

if(__name__ == "__main__"):

    to = time.time()
    sn = snAPI()
    savePTU = False
    read = False # (or write)
    if not read:
        ok = sn.getDevice()
        sn.initDevice(MeasMode.T2)
            
    size = 1024*1024*128
    numChans = sn.deviceConfig["NumChans"] + 1 
    x, sync = [],[]
    chan = [[] for _ in range(numChans)] 
    plt.show(block=False)
    
    for trigLvl in range(-50, 21):
        cnts  = [0] * sn.deviceConfig["NumChans"] + 1
        sn.device.setInputEdgeTrig(-1, trigLvl, 1)
        sn.device.setSyncEdgeTrig(trigLvl, 1)
        
        to2 =  time.time()
        if not read and savePTU:
            sn.setPTUFilePath(r"e:\data\PicoQuant\trglvl\trgLvl_" + str(trigLvl) + r".ptu")
        if read:
            sn.getFileDevice(r"e:\data\PicoQuant\trglvl\trgLvl_" + str(trigLvl) + r".ptu")
        
        sn.raw.startBlock(300, size, savePTU)
        
        while True:
            data = sn.raw.getBlock()
            finished = sn.raw.isFinished()
            if sn.raw.numRead() > 0:
                for i in range(sn.raw.numRead()):
                    if not sn.raw.isSpecial(data[i]) and not sn.raw.isMarker(data[i]):
                        chanIdx = sn.raw.channel(data[i])
                        cnts[chanIdx] += 1
                        
            if finished:
                break

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
