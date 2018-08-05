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

import RPi.GPIO as GPIO
import time
 
# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

def lcd_init():
    # Initialise display
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command
 
    GPIO.output(LCD_RS, mode) # RS
 
    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x10==0x10:
        GPIO.output(LCD_D4, True)
    if bits&0x20==0x20:
        GPIO.output(LCD_D5, True)
    if bits&0x40==0x40:
        GPIO.output(LCD_D6, True)
    if bits&0x80==0x80:
        GPIO.output(LCD_D7, True)
 
    # Toggle 'Enable' pin
    lcd_toggle_enable()
 
    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits&0x01==0x01:
        GPIO.output(LCD_D4, True)
    if bits&0x02==0x02:
        GPIO.output(LCD_D5, True)
    if bits&0x04==0x04:
        GPIO.output(LCD_D6, True)
    if bits&0x08==0x08:
        GPIO.output(LCD_D7, True)
 
    # Toggle 'Enable' pin
    lcd_toggle_enable()
 
def lcd_toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)
 
def lcd_string(message,line):
    # Send string to display
 
    message = message.ljust(LCD_WIDTH," ")
 
    lcd_byte(line, LCD_CMD)
 
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

class Azure:
    ## Variables for Azure Connection
    path_to_root_cert = "../BaltimoreCertificate/digicert.cer"
    device_id = "Receiver_WeighBridge"
    sas_token = "SharedAccessSignature sr=IWizardsIOTHub.azure-devices.net&sig=1DNvWB2XUS5al3aJi%2BXs9jMODbNJnvHpsmeGvfwbG0A%3D&se=1564663028&skn=iothubowner"
    iot_hub_name = "IWizardsIOTHub"
    azureport = 8883
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

        print("Waiting to connect to IoT Hub..")
        self.azureClient.connect(self.iot_hub_name+".azure-devices.net", self.azureport)
        self.azureClient.loop_start()

class Local:
    ''' Class to define methods, callbacks and initiate client MQTT connection to Azure IoT Hub. '''
     ## Varibales for Local Connection
    user = "Onyx"
    password = "Onyx123"
    topic = "Onyx/WeighBridge/Bridge1"
    topicWeight = "Onyx/WeighBridge/Bridge1ack"
    broker_address="BrokerPi.local"
    localport = 1883
    localClient = None

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 0):
            print ("Device connected to Local Broker.")
        else:
            print("Error code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        print ("Device disconnected from Local Broker with result code: " + str(rc))

    def on_publish(self, client, userdata, mid):
        print ("Device sent message to Weigh Bridge")
        print("Sleep for 10 seconds as buffer period")
        time.sleep(10)
        global ScanInit 
        ScanInit = True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed to receive weight")
    
    def on_message(self, client, userdata, message):
        print("Displaying Weight")
        msg = "Weight:" + str(message.payload.decode("utf-8")) + "gms"
        lcd_string(msg, LCD_LINE_1)
        lcd_string("Truck: KA03ML843", LCD_LINE_2)
 
    time.sleep(3)

    def __init__(self):
        self.localClient = mqtt.Client("WeighBridgeReceiver")
        self.localClient.on_connect = self.on_connect
        self.localClient.on_disconnect = self.on_disconnect
        self.localClient.on_publish = self.on_publish
        self.localClient.on_subscribe = self.on_subscribe

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
        while((time.time() - t0) < 3):
            rssi, address = self.rangeScanner()
            if(address == add and rssi > -45):
                prox += 1
        return prox


## Initiate the Local class
lcd_init()
Local = Local()
Local.localClient.subscribe(Local.topicWeight)
## Initialize the Azure class
Azure = Azure()

## Initiate Receiver class
Receiver = Receiver()

scanner = Scanner()

publishData = '{"id":"00815414", "DeviceID":"Receiver_WeighBridge", "EventType":"ENTRY_AUTH", "iIndustry":"true", "Devices":{ "TruckID":"111", "BLEID":"1111", "dynamic1":"11", "dynamic2":"11111" }, "Data":{}}'
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
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!",LCD_LINE_1)
        GPIO.cleanup()
        break