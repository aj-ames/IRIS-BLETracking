# IRIS: Indoor Real-time Integrated System
 #### Experimental Indoor Tracking using BLE beacons

## Setup

Use [MosquittoSetup.md](https://github.com/aj-ames/IRIS-BLETracking/blob/master/MQTTPythonSetup.md) to setup Mosquitto broker on linux.

Use [MQTTPythonSetup.md](https://github.com/aj-ames/IRIS-BLETracking/blob/master/MQTTPythonSetup.md) to install PahoMQTT library for MQTTPythonSetup.

Use [DaemonProcessSetup.md](https://github.com/aj-ames/IRIS-BLETracking/blob/master/DaemonProcessSetup.md) to setup each BLE Receiver Pi to run the Scanner script as a Daemon process.

Run the following command for easy installation of all required packages:
```sh
pip3 install -r requirements.txt
```
## Topic Names
 
### Different topic names used are as follows:

#### Boom Barrier
-  **Onyx/BoomBarrier/EntryExit**: For sending control commands to Boom Barrier at the Entry/Exit
- **Onyx/BoomBarrier/EntryExitack**: To receive acknowledgements from the Boom Barrier at the Entry/Exit
- **Onyx/BoomBarrier/Parking**: For sending control commands to Boom Barrier at the Parking Area
- **Onyx/BoomBarrier/Parkingack**: To receive acknowledgements from the Boom Barrier at the Parking Area

#### Weigh Bridge
- **Onyx/WeighBridge/Bridge1**: To send control commands to Weigh Bridge 1
- **Onyx/WeighBridge/Bridge1ack**: To get the weight back from Weigh Bridge 1
- **Onyx/WeighBridge/Bridge2**: To send control commands to Weigh Bridge 2
- **Onyx/WeighBridge/Bridge2ack**: To get the weight back from Weigh Bridge 2

#### Loading/Unloading Bays
- **Onyx/LoadingBay/Bay1**: To send control commands to Loading Bay 1
- **Onyx/LoadingBay/Bay1ack**: To receive acknowledgements from Loading Bay 1
- **Onyx/LoadingBay/Bay2**: To send control commands to Loading Bay 2
- **Onyx/LoadingBay/Bay2ack**: To receive acknowledgements from Loading Bay 2

#### Lights
- **Onyx/Lights/WeighLights**: To turn on Weigh Bridge Lights
- **Onyx/Lights/SamplingLights**: To turn on Sampling Area Lights Lights
- **Onyx/Lights/LoadingLights**: To turn on Loading Bay Lights