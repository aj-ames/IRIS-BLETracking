"""Python script to detect BLE Beacons in proximity and check for authenticity"""

import time
import math

## For using BLE
from bluepy.btle import Scanner
scanner = Scanner()

def calculateDistance(rssi):
    ## Method to calculate distance based on RSSI value
    txPower = -61
    if (rssi == 0):
        return -1.0
    
    ratio = rssi*1.0/txPower
    if (ratio < 1.0):
        return math.pow(ratio, 10)
    else:
        distance =  (0.89976) * math.pow(ratio, 7.7095) + 0.111    
        return distance

def main():
    while 1:
        try:
            devices = scanner.scan(0.25)
            for dev in devices:
                ##if(dev.addr == "55:46:4f:d3:6b:67" or dev.addr == "55:46:4f:d3:41:62" or \
                  ## dev.addr == "55:46:4f:fb:39:56" or dev.addr == "55:46:4f:fb:39:6e" or \
                  ## dev.addr == "55:46:4f:fb:6b:a2" or dev.addr == "55:46:4f:fb:39:53"):
                ##if(dev.addr == "34:15:13:cd:a5:68"):
                if(dev.addr == "55:46:4f:fb:39:6e"):
                    print("Device %s (%s), RSSI=%d dB, Distance=%f" % (dev.addr, dev.addrType, dev.rssi, calculateDistance(dev.rssi)))
            time.sleep(0.25)
        except KeyboardInterrupt:
            print("Terminated")

if __name__ == "__main__":
    main()
