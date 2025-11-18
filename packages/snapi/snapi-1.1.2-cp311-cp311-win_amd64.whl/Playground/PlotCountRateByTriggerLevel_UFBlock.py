import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from snAPI.Main import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg',force=True)
print("Switched to:",matplotlib.get_backend())
import time

if (__name__ == "__main__"):

    to = time.time()
    sn = snAPI()
    
    cppFilter = True
    savePTU = False
    read = False # (or write)

    if not read:
        ok = sn.getDevice()
        sn.initDevice(MeasMode.T2)

    size = 1024*1024*128
    numChans = sn.deviceConfig["NumChans"] + 1 + 3
    x, sync = [],[]
    chan = [[] for _ in range(numChans)]
    plt.show(block=False)
    hChans = sn.manipulators.herald(0, [1,2], 66000, 100000)
    ci = sn.manipulators.coincidence([hChans[0], hChans[1]], 10000)
    
    while True:
        for trigLvl in range(-30, 30):
            cnts  = [0] * numChans
            sn.device.setInputEdgeTrig(-1, trigLvl, 1)
            sn.device.setSyncEdgeTrig(trigLvl, 1)
            
            #hChans = sn.manipulators.herald(0, [1,2], 66000, 100000)
            #ci = sn.manipulators.coincidence([hChans[0], hChans[1]], 10000)

            to2 =  time.time()
            if not read and savePTU:
                sn.setPTUFilePath(r"e:\data\PicoQuant\trglvl\trgLvl_" + str(trigLvl) + r".ptu")
            if read:
                sn.getFileDevice(r"e:\data\PicoQuant\trglvl\trgLvl_" + str(trigLvl) + r".ptu")

            # sn.manipulators.clearAll()
            
            sn.unfold.startBlock(500, size, savePTU)
            while True:
                times, channels = sn.unfold.getBlock()
                if sn.unfold.numRead() > 0:
                    if cppFilter:
                        for i in range(numChans):
                            times = sn.unfold.getTimesByChannel(i)
                            cnts[i] += len(times)

                    else:
                        for i in range(sn.unfold.numRead()):
                            if not sn.unfold.isMarker(channels[i]):
                                chanIdx = sn.unfold.channel(channels[i])
                                cnts[chanIdx] += 1

                if sn.unfold.isFinished() and not sn.unfold.numRead() > 0:
                    break
                
            # sn.manipulators.clearAll()
            
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

            if read:
                sn.closeDevice()

    print(time.time()-to)
    
    sn.manipulators.clearAll()

    plt.show(block=True)  
