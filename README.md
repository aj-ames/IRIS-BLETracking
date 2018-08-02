# Onyx-BLETracking
 #### Experimental Indoor Tracking using BLE beacons

## Setup

Use [MosquittoSetup.md](https://gitlab.com/aj-ames/Onyx-BLETracker/blob/master/MosquittoSetup.md) to setup Mosquitto broker on linux.

Use [MQTTPythonSetup.md](https://gitlab.com/aj-ames/Onyx-BLETracker/blob/master/MQTTPythonSetup.md) to install PahoMQTT library for MQTTPythonSetup.

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