/* NodeMCU 12E program to initiate weigh scale over MQTT*/

#include <PubSubClient.h>
#include <ESP8266WiFi.h>
#define BAUD_RATE 115200

//For Weighing Scale
#include <HX711.h>

#define DOUT 12
#define CLK  14

HX711 scale(DOUT, CLK);
float calibration_factor = 780;
float units;
#define MQTT_SERVER "Kratos.local"
const char* ssid = "Onyx";
const char* password = "astr1x2096";
const char* mqtt_username = "Onyx";
const char* mqtt_password = "Onyx123";

// Topic to subscribe to for the commands
char* subTopic = "Onyx/WeighBridge/Bridge1";

// Topic to publish to confirm that the boombarrier has been turned on for the python script to log
char* pubTopic = "Onyx/WeighBridge/Bridge1ack";

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
  //weigh();
}


// MQTT callback function
void callback(char* topic, byte* payload, unsigned int length) {
  String msg = "";
  for(int i = 0; i < length; i++)
    msg += (char)payload[i];
  Serial.println(msg);
  if(msg == "weigh")
    weigh();
  yield(); //to prevent watchdog timer to run out
}

void reconnect() {

  //attempt to connect to the wifi if connection is lost
  if(WiFi.status() != WL_CONNECTED) {

    //loop while we wait for connection
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
       Serial.print(".");
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
        //weigh();
      }
    }
  }
}

void weigh() {
  // Method to calculate weight
  float temp;
  delay(100);
  temp = scale.get_units(), 10;
  Serial.println(temp);
  while(temp < 20.0) {
    temp = scale.get_units(), 10;
    delay(250);
  }
  delay(2000);
  long timer = millis();
  int counter = 0;
  Serial.print("Reading: ");
  units = scale.get_units(), 1;
  if (units < 0) {
    units = 0.00;
  }
  Serial.print(units);
  Serial.print(" grams"); 
  Serial.print(" calibration_factor: ");
  Serial.print(calibration_factor);
  Serial.println();
  String str = String(units);
  str.toCharArray(msg, str.length() + 1);
  client.publish(pubTopic, msg);
  
}


