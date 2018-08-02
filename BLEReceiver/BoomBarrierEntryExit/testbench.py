''' Python Script to enable RPi as a BLE Receiver and send data to Azure IoT Hub. '''
#!/usr/bin/python3
import ssl
import time
import math
## For MQTT
import paho.mqtt.client as mqtt
import argparse
import sys
## For using BLE
##from bluepy.btle import Scanner
##scanner = Scanner()

class Variables:
    ''' Class to store all variables used. '''

    ## Variables for Azure Connection
    path_to_root_cert = "../BaltimoreCertificate/digicert.cer"
    device_id = "DG_INOUT"
    sas_token = "SharedAccessSignature sr=IWizardsIOTHub.azure-devices.net&sig=1DNvWB2XUS5al3aJi%2BXs9jMODbNJnvHpsmeGvfwbG0A%3D&se=1564663028&skn=iothubowner"
    iot_hub_name = "IWizardsIOTHub"
    azureport = 8883
    
    ## Varibales for Local Connection
    user = "astr1x"
    password = "astr1x2096"
    topic = "Onyx/BoomBarrier/EntryExit"
    broker_address="localhost"
    localport = 1883

    ## Client Objects for MQTT
    azureClient = None
    localClient = None

    ## Template for JSON to be published
    publishData = '{"ReceiverID":"null", "EventType":"null", "Devices":{"TruckID":"null", "BLEID":"null", "dynamic1":"null", "dynamic2":"null"}}'

class Azure:
    ''' Class to define methods, callbacks and initiate client MQTT connection to Azure IoT Hub. '''

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 0):
            print ("Device connected to Azure IoT Hub.")
        else:
            print("Error code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        print ("Device disconnected from Azure IoT Hub with result code: " + str(rc))

    def on_publish(self, client, userdata, mid):
        print ("Device sent message to Azure IoT Hub")
        Variables.azureClient.subscribe("devices/" + Variables.device_id + "/messages/devicebound/#")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed")

    def on_message(self, client, userdata, message):
        print("Device received message from Azure IoT Hub")
        print(str(message.payload.decode("utf-8")))

    def __init__(self):
        Variables.azureClient = mqtt.Client(client_id=Variables.device_id, 
                                            protocol=mqtt.MQTTv311)
        Variables.azureClient.on_connect = self.on_connect
        Variables.azureClient.on_disconnect = self.on_disconnect
        Variables.azureClient.on_publish = self.on_publish
        Variables.azureClient.on_subscribe = self.on_subscribe
        Variables.azureClient.on_message = self.on_message

        print("Initiating connection to Azure IoT Hub..")
        Variables.azureClient.username_pw_set(username=Variables.iot_hub_name 
                                              +".azure-devices.net/"
                                              +Variables.device_id, 
                                              password=Variables.sas_token)

        Variables.azureClient.tls_set(ca_certs=Variables.path_to_root_cert,
                                      certfile=None, keyfile=None,
                                      cert_reqs=ssl.CERT_REQUIRED, 
                                      tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
        Variables.azureClient.tls_insecure_set(False)

        print("Waiting to connect to IoT Hub..")
        Variables.azureClient.connect(Variables.iot_hub_name+".azure-devices.net", Variables.azureport)
        Variables.azureClient.loop_start()


class Local:
    ''' Class to define methods, callbacks and initiate client MQTT connection to Azure IoT Hub. '''

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 0):
            print ("Device connected to Local Broker.")
        else:
            print("Error code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        print ("Device disconnected from Local Broker with result code: " + str(rc))

    def on_publish(self, client, userdata, mid):
        print ("Device sent message to Boom Barrier")

    def __init__(self):
        Variables.localClient = mqtt.Client("BoomBarrierReceiver")
        Variables.localClient.on_connect = self.on_connect
        Variables.localClient.on_disconnect = self.on_disconnect
        Variables.localClient.on_publish = self.on_publish

        print("Initializing connection to Local Broker")
        Variables.localClient.username_pw_set(Variables.user, password=Variables.password)  # set username and password
        Variables.localClient.connect(Variables.broker_address, Variables.localport)  # connect to broker
        Variables.localClient.loop_start()
        
'''
class Receiver:
    def calculateDistance(self, rssi):
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

    def rangeScanner(self):
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

    def proximityScanner(self, add):
        """ Method to quantify if beacon is in proximity. """
        t0 = time.time()
        while((time.time() - t0) < 4):
            rssi, address = self.rangeScanner()
            if(address == None and rssi == 0):
                return None
            elif(address == add and rssi > -34 and rssi < 0):
                pass
        return add
'''

## Initialize the Azure class
Azure()

## Initiate the Local class
Local()

Variables.azureClient.publish("devices/" + Variables.device_id + "/messages/events/",
                          Variables.publishData, qos=1)
Variables.localClient.publish(Variables.topic, "Yo", qos=1)

try:
    while True:
        time.sleep(0.1)
except (KeyboardInterrupt, SystemExit):
    print()
    print("Exiting..")
    Variables.localClient.loop_stop()
    Variables.localClient.disconnect()
    Variables.azureClient.loop_stop()
    Variables.azureClient.disconnect()
