/* NodeMCU 12E program to open and close boom barrier over MQTT*/
#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#define BAUD_RATE 9600

// For Servo Motor
#include <Servo.h>
Servo servo;
#define servopin D4

// For ultrasonic
#define TRIGGER D1
#define ECHO    D2

// FOR RGB
#define red D7
#define green D8

#define MQTT_SERVER "Kratos.local"
const char* ssid = "Onyx";
const char* password = "astr1x2096";
const char* mqtt_username = "Onyx";
const char* mqtt_password = "Onyx123";

// Topic to subscribe to for the commands
char* subTopic = "Onyx/BoomBarrier/EntryExit";

// Topic to publish to confirm that the boombarrier has been turned on for the python script to log
char* pubTopic = "Onyx/BoomBarrier/EntryExitack";

String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete

// Callback function header
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void servoControl(String cmd);
long ultrasonic();
void serialEvent();

WiFiClient wifiClient;
PubSubClient client(MQTT_SERVER, 1883, callback, wifiClient);

void setup() {
  // Start the serial line for debugging
  Serial.begin(BAUD_RATE);
  delay(100);

  servo.attach(servopin);
  servo.write(0);
  delay(500);
  servo.detach();

  //fps.Open();         //send serial command to initialize fps
  //fps.SetLED(true);   //turn on LED so fps can see fingerprint

  pinMode(TRIGGER, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);

  // Start wifi subsystem
  WiFi.begin(ssid, password);

  // Attempt to connect to the WIFI network and then connect to the MQTT server
  reconnect();

  // Wait a bit before starting the main loop
  delay(2000);
  Serial.println("Done");
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
  for (int i = 0; i < length; i++)
    msg += (char)payload[i];
  servoControl(msg);
  yield(); //to prevent watchdog timer to run out
}


//networking functions

void reconnect() {

  //attempt to connect to the wifi if connection is lost
  if (WiFi.status() != WL_CONNECTED) {

    //loop while we wait for connection
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
    }
  }

  //make sure we are connected to WIFI before attemping to reconnect to MQTT
  if (WiFi.status() == WL_CONNECTED) {
    // Loop until we're reconnected to the MQTT server
    while (!client.connected()) {

      // Generate client name based on MAC address and last 8 bits of microsecond counter
      String clientName;
      clientName += "BoomBarrierEntryExit";

      //if connected, subscribe to the topic(s) we want to be notified about
      if (client.connect((char*) clientName.c_str(), mqtt_username, mqtt_password)) {
        client.subscribe(subTopic);
      }
    }
  }
}

void servoControl(String command)
{
  if(command == "open") {
    Serial.print("scan:");
    long timer = millis();
    while(millis() - timer <= 5000) {
      yield();
      serialEvent();
      if(stringComplete)
        break;
    }
    if(stringComplete && inputString == "Authorized") {
      servo.attach(servopin);
      servo.write(90);
      delay(500);
      servo.detach();
      while(true) {
        if(ultrasonic() < 10)
        {
          delay(250);
          while(ultrasonic() < 10)
            delay(250);
          break; 
        }
      }
      delay(1000);
      servo.attach(servopin);
      servo.write(0);
      delay(500);
      servo.detach();
    }
    stringComplete = false;
    inputString = "";
  }
  if (command == "close") {
    servo.attach(servopin);
    servo.write(0);
    delay(500);
    servo.detach();
  }
}
long ultrasonic()
{
  long duration, distance;
  digitalWrite(TRIGGER, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIGGER, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIGGER, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = (duration / 2) / 29.1;
  return distance;
}

void serialEvent() {
  while(Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == ':') {
      stringComplete = true;
      break;
    }
    inputString += inChar;
  }
}

