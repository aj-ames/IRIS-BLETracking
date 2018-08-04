""" Python script to publish the Beacon Address to Azure IoT Hub. """
#!/usr/bin/python3

## To utilize MQTT
from paho.mqtt import client as mqtt

import ssl
import time
import argparse

path_to_root_cert = "../../BaltimoreCertificate/digicert.cer"
device_id = "BLE_Parking"
sas_token = "SharedAccessSignature sr=IWizardsIOTHub.azure-devices.net&sig=1DNvWB2XUS5al3aJi%2BXs9jMODbNJnvHpsmeGvfwbG0A%3D&se=1564663028&skn=iothubowner"
iot_hub_name = "IWizardsIOTHub"

## Template for JSON to be published
publishData = '{"ReceiverID":"null", "EventType":"null", "Devices":{"TruckID":"null", "BLEID":"null", "dynamic1":"null", "dynamic2":"null"}}'

def on_connect(client, userdata, flags, rc):
    client.subscribe("devices/" + device_id + "/messages/devicebound/#")
    print ("Device connected with result code: " + str(rc))

def on_disconnect(client, userdata, rc):
    print ("Device disconnected with result code: " + str(rc))

def on_publish(client, userdata, mid):
    print ("Device sent message")

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed")

def on_unsubscribe(client, userdata, mid):
    print("Unsubscribed")

def on_message(client, userdata, message):
    print(str(message.payload.decode("utf-8")))
    client.disconnect()

def get_args_values(args=None):
    """Method to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Arguments supported..")
    parser.add_argument('-m', '--message',
                        help='Message to be published',
                        default='{"null":"null"}')

    info = parser.parse_args(args)
    return (info.message)

def JSONGenerator(value, pos):
    return (publishData.replace('null', value, pos))

client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscribe
client.on_message = on_message

print("Initiating..")
client.username_pw_set(username=iot_hub_name+".azure-devices.net/" + device_id, password=sas_token)

client.tls_set(ca_certs=path_to_root_cert, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
client.tls_insecure_set(False)

print("Waiting to connect..")
client.connect(iot_hub_name+".azure-devices.net", port=8883)

client.publish("devices/" + device_id + "/messages/events/", publishData, qos=1)
client.loop_forever()
print()
print("Exiting..")
