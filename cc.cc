#include <DHT.h>

// ==========================
// RELAY PINS
// ==========================
const int relayAircon = 8;
const int relayLamp = 9;
const int relayLights = 10;
const int relayTV = 11;

// ==========================
// DHT SETTINGS
// ==========================
#define DHTTYPE DHT11
#define DHTPIN 2

DHT dht(DHTPIN, DHTTYPE);


// ==========================
// INITIALIZE RELAYS (ACTIVE LOW)
// ==========================
void initializeRelays() {
  pinMode(relayAircon, OUTPUT);
  pinMode(relayLamp, OUTPUT);
  pinMode(relayLights, OUTPUT);
  pinMode(relayTV, OUTPUT);

  digitalWrite(relayAircon, HIGH);
  digitalWrite(relayLamp, HIGH);
  digitalWrite(relayLights, HIGH);
  digitalWrite(relayTV, HIGH);
}


// ==========================
// PROCESS COMMANDS
// ==========================
void processCommand(String command) {

  if (command == "airconon") digitalWrite(relayAircon, LOW);
  else if (command == "airconoff") digitalWrite(relayAircon, HIGH);

  else if (command == "lampon") digitalWrite(relayLamp, LOW);
  else if (command == "lampoff") digitalWrite(relayLamp, HIGH);

  else if (command == "lightson") digitalWrite(relayLights, LOW);
  else if (command == "lightsoff") digitalWrite(relayLights, HIGH);

  else if (command == "tvon") digitalWrite(relayTV, LOW);
  else if (command == "tvoff") digitalWrite(relayTV, HIGH);

  else if (command == "allon") {
    digitalWrite(relayAircon, LOW);
    digitalWrite(relayLamp, LOW);
    digitalWrite(relayLights, LOW);
    digitalWrite(relayTV, LOW);
  }

  else if (command == "alloff") {
    digitalWrite(relayAircon, HIGH);
    digitalWrite(relayLamp, HIGH);
    digitalWrite(relayLights, HIGH);
    digitalWrite(relayTV, HIGH);
  }

  // 🔥 Temperature request from Python
  else if (command == "get_temp") {
    float tempC = dht.readTemperature();

    if (isnan(tempC)) {
      Serial.println("Temperature: 0");
    } else {
      Serial.print("Temperature: ");
      Serial.println(tempC);
    }
  }
}


// ==========================
// SETUP
// ==========================
void setup() {
  Serial.begin(9600);
  dht.begin();
  initializeRelays();
}


// ==========================
// LOOP
// ==========================
void loop() {

  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    processCommand(command);
  }
}
