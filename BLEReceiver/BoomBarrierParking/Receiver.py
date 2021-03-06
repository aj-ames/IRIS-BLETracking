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

from bluepy.btle import Scanner

## Flag to check acknowledgement
SendAck = False
ScanInit = True

class Azure:
    ## Variables for Azure Connection
    path_to_root_cert = "../BaltimoreCertificate/digicert.cer"
    device_id = "Receiver_Parking"
    sas_token = "SharedAccessSignature sr=IWizardsIOTHub.azure-devices.net&sig=1DNvWB2XUS5al3aJi%2BXs9jMODbNJnvHpsmeGvfwbG0A%3D&se=1564663028&skn=iothubowner"
    iot_hub_name = "IWizardsIOTHub"
    azureport = 8883
    head = {
        "iothub-contenttype":"application/json",
        "iothub-contentencoding":"utf-8"
    }
    azureClient = None

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
        self.azureClient.subscribe("devices/" + self.device_id + "/messages/devicebound/#")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed")

    def on_message(self, client, userdata, message):
        print("Device received message from Azure IoT Hub")
        global Local
        Local.localClient.publish(Local.topic, "open", qos=1)
        time.sleep(1)
        Local.localClient.publish(Local.topicCheck, Local.allowed, qos=1)

    def __init__(self):
        self.azureClient = mqtt.Client(client_id=self.device_id, 
                                            protocol=mqtt.MQTTv311)
        self.azureClient.on_connect = self.on_connect
        self.azureClient.on_disconnect = self.on_disconnect
        self.azureClient.on_publish = self.on_publish
        self.azureClient.on_subscribe = self.on_subscribe
        self.azureClient.on_message = self.on_message

        print("Initiating connection to Azure IoT Hub..")
        self.azureClient.username_pw_set(username=self.iot_hub_name 
                                              +".azure-devices.net/"
                                              +self.device_id, 
                                              password=self.sas_token)

        self.azureClient.tls_set(ca_certs=self.path_to_root_cert,
                                      certfile=None, keyfile=None,
                                      cert_reqs=ssl.CERT_REQUIRED, 
                                      tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
        self.azureClient.tls_insecure_set(False)
        self.azureClient.ws_set_options(path="/mqtt", headers=self.head)
        print("Waiting to connect to IoT Hub..")
        self.azureClient.connect(self.iot_hub_name+".azure-devices.net", self.azureport)
        self.azureClient.loop_start()

class Local:
    ''' Class to define methods, callbacks and initiate client MQTT connection to Azure IoT Hub. '''
     ## Varibales for Local Connection
    user = "Onyx"
    password = "Onyx123"
    topic = "Onyx/BoomBarrier/Parking"
    topicCheck = "Onyx/BoomBarrier/Parkingack"
    broker_address="Kratos.local"
    localport = 1883
    localClient = None
    allowed = None

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 0):
            print ("Device connected to Local Broker.")
        else:
            print("Error code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        print ("Device disconnected from Local Broker with result code: " + str(rc))

    def on_publish(self, client, userdata, mid):
        print ("Device sent message to Boom Barrier")
        print("Sleep for 10 seconds as buffer period")
        time.sleep(10)
        global ScanInit 
        ScanInit = True

    def __init__(self):
        self.localClient = mqtt.Client("BoomParkingReceiver")
        self.localClient.on_connect = self.on_connect
        self.localClient.on_disconnect = self.on_disconnect
        self.localClient.on_publish = self.on_publish

        print("Initializing connection to Local Broker")
        self.localClient.username_pw_set(self.user, password=self.password)  # set username and password
        self.localClient.connect(self.broker_address, self.localport)  # connect to broker
        self.localClient.loop_start()
        
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
        print("Scanning..")
        global scanner
        devices = scanner.scan(1)
        rssi = -45
        address = None
        for dev in devices:
            if(dev.rssi > rssi):
                rssi = dev.rssi
                address = dev.addr
        if(not address == None):
            print("Within Range: " + address + "RSSI: " + str(rssi))
        time.sleep(0.25)
        return rssi, address

    def proximityScanner(self, add):
        """ Method to quantify if beacon is in proximity. """
        prox = 0
        t0 = time.time()
        while((time.time() - t0) < 4):
            rssi, address = self.rangeScanner()
            if(address == add and rssi > -45):
                prox += 1
                if(prox == 2):
                    global Local
                    Local.allowed = address
                    break
        return prox


## Initiate the Local class
Local = Local()
## Initialize the Azure class
Azure = Azure()

## Initiate Receiver class
Receiver = Receiver()

scanner = Scanner()

publishData = '{"id":"00815414", "DeviceID":"Receiver_Parking", "EventType":"ENTRY_AUTH", "iIndustry":"true", "Devices":{ "TruckID":"111", "BLEID":"1111", "dynamic1":"11", "dynamic2":"11111" }, "Data":{}}'

while True:
    result = None
    try:
        if(ScanInit):
            rssi, address = Receiver.rangeScanner()
            if(rssi > -45):
                result = Receiver.proximityScanner(address)
                if(result >= 2):
                    Azure.azureClient.publish("devices/" + Azure.device_id + "/messages/events/",
                                               publishData, qos=1)
                    ScanInit = False
    except (KeyboardInterrupt, SystemExit):
        print()
        print("Exiting..")
        Local.localClient.loop_stop()
        Local.localClient.disconnect()
        Azure.azureClient.loop_stop()
        Azure.azureClient.disconnect()
        break