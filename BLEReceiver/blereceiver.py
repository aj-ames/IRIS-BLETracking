"""Python script to detect BLE Beacons in proximity and check for authenticity"""
#!/usr/bin/python3
import time
import math
## For MQTT
import paho.mqtt.client as mqtt
import argparse
import sys
## For using BLE
from bluepy.btle import Scanner
scanner = Scanner()

## All UFO beacon addresses
ufo = ["55:46:4f:d3:6b:67", "55:46:4f:d3:41:62", 
       "55:46:4f:fb:39:56", "55:46:4f:fb:39:6e",
       "55:46:4f:fb:6b:a2", "55:46:4f:fb:39:53"]

def get_args_values(args=None):
    """Method to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Arguments supported..")
    parser.add_argument('-H', '--host',
                        help='Broker IP',
                        default='localhost')
    parser.add_argument('-p', '--port',
                        help='port of the Broker',
                        default='1883')
    parser.add_argument('-u', '--user',
                        help='user name',
                        default='astr1x')
    parser.add_argument('-P', '--password',
                        help="password",
                        default="astr1x2096")
    parser.add_argument('-topic', '--topic',
                        help="topic to publish",
                        default='onyx')

    info = parser.parse_args(args)
    return (info.host,
            info.port,
            info.user,
            info.password,
            info.topic)


def calculateDistance(rssi):
    """ Method to calculate distance based on RSSI value. """
    txPower = -61
    if (rssi == 0):
        return -1.0
    
    ratio = rssi*1.0/txPower
    if (ratio < 1.0):
        return math.pow(ratio, 10)
    else:
        distance =  (0.89976) * math.pow(ratio, 7.7095) + 0.111    
        return distance

def rangeScanner():
    """ Method to check for beacons in range. """
    devices = scanner.scan(0.5)
    for dev in devices:
        if(dev.addr == "55:46:4f:fb:39:6e" and dev.rssi > -34):
            print("Within Range")
            time.sleep(0.25)
            return dev.rssi, dev.addr
    print("Out of bound")
    time.sleep(0.25)
    return 0, None

def proximityScanner(add):
    """ Method to quantify if beacon is in proximity. """
    t0 = time.time()
    while((time.time() - t0) < 4):
        rssi, address = rangeScanner()
        if(address == None and rssi == 0):
                return None
        elif(address == add and rssi > -34 and rssi < 0):
            pass
    return add

if __name__ == '__main__':
    broker_address, port, user, password, topic = get_args_values(sys.argv[1:])
    port = int(port)

    client = mqtt.Client()
    client.username_pw_set(user, password=password)  # set username and password
    client.connect(broker_address, port)  # connect to broker

    while True:
        result = None
        try:
            rssi, address = rangeScanner()
            if(rssi > -34 and rssi < 0):
                result = proximityScanner(address)
            if(result == None):
                pass
            else:
                print("Authenticated: ", result)
                client.publish(topic, result, qos=1, retain=True)
                time.sleep(5)
        except (KeyboardInterrupt, SystemExit):
            break
    client.disconnect()
    print()
    print("Exiting..")