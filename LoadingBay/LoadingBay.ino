/* NodeMCU 12E program to initiate loading bay over MQTT */

#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#define BAUD_RATE 9600

// For motor driver
#define in1 D1
#define in2 D2

// For HC-SR04 sensor
int trigPin = D7;
int echoPin = D8;

#define MQTT_SERVER "Kratos.local"
const char* ssid = "SpectraNet_iWiz";
const char* password = "iWizards2014";
const char* mqtt_username = "Onyx";
const char* mqtt_password = "Onyx123";

// Topic to subscribe to for the commands
char* subTopic = "Onyx/LoadingBay/Bay1";

// Topic to publish to confirm that the loadingbay has been turned on for the python script to log
char* pubTopic = "Onyx/LoadingBay/Bay1ack";

// Callback function header
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
bool distanceCalculator();
bool verifyProximity();
void loader(String command);

WiFiClient wifiClient;
PubSubClient client(MQTT_SERVER, 1883, callback, wifiClient);

void setup() {
  Serial.begin(BAUD_RATE);
  delay(100);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  // Set initial rotation direction
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  delay(100);

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
  for(int i = 0; i < length; i++)
    msg += (char)payload[i];
  loader(msg);
  yield(); //to prevent watchdog timer to run out
}

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
      clientName += "LoadingBay";

      //if connected, subscribe to the topic(s) we want to be notified about
      if (client.connect((char*) clientName.c_str(), mqtt_username, mqtt_password)) {
        //Serial.print("\tMQTT Connected");
        client.subscribe(subTopic);
      }
    }
  }
}

bool distanceCalculator() {
  // Method to calculate distance
  digitalWrite(trigPin, LOW); // low pulse first to ensure a clean high pulse.
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  delayMicroseconds(10);
  float echoTime = pulseIn (echoPin, HIGH);
  delayMicroseconds(10);
  float distance = (echoTime * 0.034) / 2;
  Serial.println(distance);
  if(distance < 10)
    return true;
  else
    return false;
}

bool verifyProximity() {
  // Method to check if beacon is in proper range
  int timer = millis();
  while((millis() - timer) < 3000) { 
    if(!distanceCalculator()) {
      return false;
    }
  }
  return true;
}

void loader(String cmd) {
  // Method to start loading
  if(cmd == "load") {
    Serial.println("Checking proximity");
    if(verifyProximity()) {
      Serial.println("Starting to Load");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      delay(3000);
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      delay(100);
    }
  }
}

