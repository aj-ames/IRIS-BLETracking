# Mosquitto broker setup on linux system

### Mosquitto broker and client can be installed by the following commands:

```sh
sudo apt update
sudo apt install mosquitto mosquitto-clients
```
#### 1. Testing the client

Open two different terminals. One will be used to publish and another to subscribe to the publication.
The topic used will be "topic".

To subscribe:
```sh
mosquitto_sub -t "topic"
```
To publish to "topic":
```sh
mosquitto_pub -m "message from mosquitto_pub client" -t "topic"
```

#### 2. Password security
Set password in the following manner:
```sh
sudo mosquitto_passwd -c /etc/mosquitto/passwd username # replace username with a name you want
Password: password
Confirm Password: password
```

Create a configuration file for Mosquitto pointing to the password file we have just created.
```sh
sudo nano /etc/mosquitto/conf.d/default.conf
```

Enter the following lines in it:
```sh
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Remember to restart the mosquitto service
```sh
sudo systemctl restart mosquitto
```

Publish and Subscribe with the following commands:
```sh
mosquitto_sub -t "topic" -u "username" -P "password"
mosquitto_pub -t "topic" -m "message" -u "username" -P "password"
```
