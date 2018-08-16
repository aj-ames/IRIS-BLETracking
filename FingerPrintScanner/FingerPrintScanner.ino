#define BAUD_RATE 9600

// For fingerprint scanner
#include<FPS_GT511C3.h>
#include<SoftwareSerial.h>
FPS_GT511C3 fps(A8, A9);

char msg[100];

bool scanInit();
void fingScan();
//void serialEvent1();

String inputString = "";         // a String to hold incoming data
boolean stringComplete = false;  // whether the string is complete


void setup() {
  Serial.begin(BAUD_RATE); //set up Arduino's hardware serial UART
  Serial1.begin(BAUD_RATE);
  delay(100);
  Serial.println("Mega Ready!");
}

void loop() {
  if (stringComplete) {
    fingScan();
  }
}

bool scanInit() {
  fps.CaptureFinger(false);
  int id = fps.Identify1_N();
  if (id < 20)
    return true;
  return false;
}

void fingScan() {
  fps.Open();
  long timer = millis();
  if(inputString == "scan") {
    while(millis() - timer <= 3000) {
      fps.SetLED(true);
      delay(100);  
      if(fps.IsPressFinger()) {
        if(scanInit()) {
          Serial.println("Authorized:");
          Serial1.print("Authorized:");
          break;
        }
        else {
          Serial.println("Unauthorized:");
          Serial1.print("Authorized:");
          break;
        }
      }
      fps.SetLED(false);
      delay(100);
    }
  }
  stringComplete = false;
  inputString = "";
  fps.SetLED(false);
  fps.Close();
}

void serialEvent1() {
  while(Serial1.available()) {
    char inChar = (char)Serial1.read();
    if (inChar == ':') {
      stringComplete = true;
      Serial.println(inputString);
      break;
    }
    inputString += inChar;
  }
}

