# Setting up BLE Scanner script as Daemon Process

### 1. Create shell script

Create a shell script of the python file that needs to be executed:
```sh
sudo nano run.sh
```
In the script put the following lines:
```sh
#!/bin/sh
cd /home/pi/IRIS-BLETracking/BLEReceiver/<The type of Receiver>
sudo python3 Receiver.py
```
Save the contents of this file.

### 2. Create the service file

Create the file with the follwing command: 
```sh
sudo nano /lib/systemd/system/ble.service
```
Add the follwing content in the file:
```
 [Unit]
 Description=My BLE Service
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=/bin/sh /home/pi/run.sh

 [Install]
 WantedBy=multi-user.target
 ```
Save the contents of the file

Change the permissions of the file to 644:
```sh
sudo chmod 644 /lib/systemd/system/ble.service
```

### 3. Configure systemd
Run the following commands:
```sh
## To reload daemons cause a new one has been created
sudo systemctl daemon-reload 
## To start the service 
sudo systemctl start ble.service
```

Once done, reboot the Pi:
```sh
sudo reboot
```

**Note:** You can stop or restart the service with the following commands:
```sh
## To stop
sudo systemctl stop ble.service
## To restart
sudo systemctl restart ble.service