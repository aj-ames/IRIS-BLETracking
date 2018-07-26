/* NodeMCU 12E program to open and close boom barrier over MQTT*/

#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#define BAUD_RATE 9600

// For Servo Motor
#include <Servo.h>
Servo servo;
#define servopin D4

#define MQTT_SERVER "192.168.0.2"
const char* ssid = "Onyx";
const char* password = "astr1x2096";
const char* mqtt_username = "Onyx";
const char* mqtt_password = "Onyx123";

// Topic to subscribe to for the commands
char* subTopic = "Onyx/BoomBarrier/EntryExit";

// Topic to publish to confirm that the boombarrier has been turned on for the python script to log
char* pubTopic = "Onyx/BoomBarrier/EntryExitack";

// Callback function header
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void servoControl(String cmd);

WiFiClient wifiClient;
PubSubClient client(MQTT_SERVER, 1883, callback, wifiClient);

void setup() {
  // Start the serial line for debugging
  Serial.begin(BAUD_RATE);
  delay(100);

  servo.attach(servopin);
  servo.write(0);
  delay(250);
  servo.detach();

  // Start wifi subsystem
  WiFi.begin(ssid, password);

  // Attempt to connect to the WIFI network and then connect to the MQTT server
  reconnect();

  // Wait a bit before starting the main loop
  delay(2000);
}

void loop() {
   // Reconnect if connection is lost
  if (!client.connected() && WiFi.status() == 3)
    reconnect();

  // Maintain MQTT connection
  client.loop();
  
  // MUST delay to allow ESP8266 WIFI functions to run
  delay(10);
}

// MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for(int i = 0; i < length; i++)
    msg += (char)payload[i];
  servoControl(msg);
  yield(); //to prevent watchdog timer to run out
}


//networking functions

void reconnect() {

  //attempt to connect to the wifi if connection is lost
  if(WiFi.status() != WL_CONNECTED) {

    //loop while we wait for connection
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      // Serial.print(".");
    }
}

  //make sure we are connected to WIFI before attemping to reconnect to MQTT
  if(WiFi.status() == WL_CONNECTED){
  // Loop until we're reconnected to the MQTT server
    while (!client.connected()) {

      // Generate client name based on MAC address and last 8 bits of microsecond counter
      String clientName;
      clientName += "BoomBarrierEntryExit";

      //if connected, subscribe to the topic(s) we want to be notified about
      if (client.connect((char*) clientName.c_str(), mqtt_username, mqtt_password)) {
        //Serial.print("\tMQTT Connected");
        client.subscribe(subTopic);
      }
    }
  }
}

void servoControl(String command) {
  if(command == "open") {
    Serial.println("opening");
    servo.attach(servopin);
    servo.write(90);
    delay(250);
    servo.detach();
  }
  if(command == "close") {
    Serial.println("closing");
    servo.attach(servopin);
    servo.write(0);
    delay(250);
    servo.detach();
  }
}

