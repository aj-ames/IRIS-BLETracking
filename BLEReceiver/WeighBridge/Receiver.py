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

import RPi.GPIO as GPIO
import smbus
import time

## Flag to check acknowledgement
SendAck = False
ScanInit = True

class Display:
    # Define some device parameters
    I2C_ADDR  = 0x3f # I2C device address, if any error, change this address to 0x27
    LCD_WIDTH = 16   # Maximum characters per line

    # Define some device constants
    LCD_CHR = 1 # Mode - Sending data
    LCD_CMD = 0 # Mode - Sending command

    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

    LCD_BACKLIGHT  = 0x08  # On
    #LCD_BACKLIGHT = 0x00  # Off

    ENABLE = 0b00000100 # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    #Open I2C interface
    #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
    bus = smbus.SMBus(1) # Rev 2 Pi uses 1
    
    def lcd_init(self):
        # Initialise display
        self.lcd_byte(0x33, self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32, self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
        self.lcd_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command

        bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        bits_low = mode | ((bits<<4) & 0xF0) | self.LCD_BACKLIGHT

        # High bits
        self.bus.write_byte(self.I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        # Low bits
        self.bus.write_byte(self.I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR,(bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def lcd_string(self, message, line):
        # Send string to display

        message = message.ljust(self.LCD_WIDTH," ")

        self.lcd_byte(line, self.LCD_CMD)

        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)
        
    
    def __init__(self):
        self.lcd_init()
        

class Azure:
    ## Variables for Azure Connection
    path_to_root_cert = "../BaltimoreCertificate/digicert.cer"
    device_id = "Receiver_WeighBridge"
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
        Local.localClient.publish(Local.topic, "weigh", qos=1)

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
    topic = "Onyx/WeighBridge/Bridge1"
    topicWeight = "Onyx/WeighBridge/Bridge1ack"
    topicLight = "Onyx/Lights/WeighLights"
    broker_address="Kratos.local"
    localport = 1883
    localClient = None
    flag = False

    def on_connect(self, client, userdata, flags, rc):
        if(rc == 0):
            print ("Device connected to Local Broker.")
        else:
            print("Error code: " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        print ("Device disconnected from Local Broker with result code: " + str(rc))

    def on_publish(self, client, userdata, mid):
        if(self.flag):
            print("Device sent message to Weigh Lights")
            print("Sleep for 10 seconds as buffer period")
            time.sleep(10)
            global ScanInit 
            ScanInit = True
            self.flag = False
            return
        print ("Device sent message to Weigh Bridge")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed to receive weight")
    
    def on_message(self, client, userdata, message):
        print("Displaying Weight")
        msg = "Weight:" + str(message.payload.decode("utf-8")) + "gms"
        global Display
        Display.lcd_string(msg, Display.LCD_LINE_1)
        Display.lcd_string("Truck: KA03ML843", Display.LCD_LINE_2)
        self.localClient.publish(self.topicLight, "light", qos=1)
        self.flag = True
 
    time.sleep(3)

    def __init__(self):
        self.localClient = mqtt.Client("WeighBridgeReceiver")
        self.localClient.on_connect = self.on_connect
        self.localClient.on_disconnect = self.on_disconnect
        self.localClient.on_publish = self.on_publish
        self.localClient.on_subscribe = self.on_subscribe
        self.localClient.on_message = self.on_message

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
        devices = scanner.scan(0.5)
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
                    break
        return prox


## Initiate the Local class
Display = Display()
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
        Display.lcd_byte(0x01, Display.LCD_CMD)
        Display.lcd_string("Goodbye!", Display.LCD_LINE_1)
        GPIO.cleanup()
        break