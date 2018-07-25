/* NodeMCU 12E program to initiate weigh scale over MQTT*/

#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#define BAUD_RATE 9600

//For Weighing Scale
#include <HX711.h>

#define DOUT 12
#define CLK  14

HX711 scale(DOUT, CLK);
float calibration_factor = 30;

#define MQTT_SERVER "192.168.0.100"
const char* ssid = "Onyx";
const char* password = "astr1x2096";
const char* mqtt_username = "astr1x";
const char* mqtt_password = "astr1x2096";

// Topic to subscribe to for the commands
char* subTopic = "WeighScale";

// Topic to publish to confirm that the boombarrier has been turned on for the python script to log
char* pubTopic = "WeighScale/ack";

char msg[100];

// Callback function header
void callback(char* topic, byte* payload, unsigned int length);
void reconnect();
void weigh();

WiFiClient wifiClient;
PubSubClient client(MQTT_SERVER, 1883, callback, wifiClient);

void setup() {
  Serial.begin(BAUD_RATE);
  delay(100);

  //Calibrating the Scale
  scale.set_scale();
  scale.tare();  //Reset the scale to 0
  delay(10);
  scale.set_scale(calibration_factor); //Adjust to this calibration factor
  delay(10);
  /*long zero_factor = scale.read_average(); //Get a baseline reading
  Serial.print("Zero factor: "); //This can be used to remove the need to tare the scale. Useful in permanent scale projects.
  Serial.println(zero_factor);*/

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
  weigh();
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
      clientName += "WeighBridge";

      //if connected, subscribe to the topic(s) we want to be notified about
      if (client.connect((char*) clientName.c_str(), mqtt_username, mqtt_password)) {
        //Serial.print("\tMQTT Connected");
        client.subscribe(subTopic);
      }
    }
  }
}

void weigh() {
  // Method to calculate weight
  float units;
  long timer = millis();
  int counter = 0;
  while((millis() - timer) < 2000) {
    units = scale.get_units(), 10;
    if (units < 0) {
      units = 0.00;
    }
    counter += 1;
    delay(100);
  }
  units = units/counter;
  String str = String(units);
  str.toCharArray(msg, str.length() + 1);
    client.publish(pubTopic, msg);
}

