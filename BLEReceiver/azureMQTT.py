""" Python script to publish the Beacon Address to Azure IoT Hub. """
#!/usr/bin/python3

## To utilize MQTT
from paho.mqtt import client as mqtt

import ssl
import time
import argparse

path_to_root_cert = "digicert.cer"
device_id = "TestBenchPiZeroW"
sas_token = "SharedAccessSignature sr=IOTHUBX-Paid.azure-devices.net%2Fdevices%2FTestBenchPiZeroW&sig=7gzSFuxNfmU9PIImPT24apVB%2FHV4mSDXDeKg7ov0y0U%3D&se=1532512324"
iot_hub_name = "IOTHUBX-Paid"

def on_connect(client, userdata, flags, rc):
    print ("Device connected with result code: " + str(rc))

def on_disconnect(client, userdata, rc):
    print ("Device disconnected with result code: " + str(rc))

def on_publish(client, userdata, mid):
    print ("Device sent message")
    client.disconnect()

def get_args_values(args=None):
    """Method to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Arguments supported..")
    parser.add_argument('-m', '--message',
                        help='Message to be published',
                        default='{"beacon_address":"null"}')

client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

print("Initiating..")
client.username_pw_set(username=iot_hub_name+".azure-devices.net/" + device_id, password=sas_token)

client.tls_set(ca_certs=path_to_root_cert, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)
client.tls_insecure_set(False)

print("Waiting to connect..")
client.connect(iot_hub_name+".azure-devices.net", port=8883)

client.publish("devices/" + device_id + "/messages/events/", , qos=1)
client.loop_forever()
print()
print("Exiting..")