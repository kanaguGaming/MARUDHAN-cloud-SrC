#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include "config.h"

WiFiClient espClient;
PubSubClient mqttClient(espClient);
Adafruit_AHTX0 aht;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (unsigned int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  // Handle commands if necessary
}

void reconnect() {
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println("connected");
      mqttClient.subscribe(MQTT_TOPIC_SUB);
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  setup_wifi();
  
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(callback);

  if (!aht.begin()) {
    Serial.println("Could not find AHT20? Check wiring");
  } else {
    Serial.println("AHT20 found");
  }
  
  pinMode(SOIL_MOISTURE_PIN, INPUT);
}

void loop() {
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.loop();

  // Non-blocking publish every 10 seconds
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 10000) {
    lastMsg = now;

    sensors_event_t humidity, temp;
    aht.getEvent(&humidity, &temp);

    int soilMoistureRaw = analogRead(SOIL_MOISTURE_PIN);
    // Simple mapping: assuming 4095 is dry and 0 is wet (adjust based on actual sensor)
    float soilMoisturePercent = map(soilMoistureRaw, 4095, 0, 0, 100);

    StaticJsonDocument<200> doc;
    doc["device_id"] = MQTT_CLIENT_ID;
    doc["temperature_c"] = temp.temperature;
    doc["humidity_percent"] = humidity.relative_humidity;
    doc["soil_moisture_percent"] = soilMoisturePercent;

    char out[256];
    serializeJson(doc, out);

    Serial.print("Publishing message: ");
    Serial.println(out);
    mqttClient.publish(MQTT_TOPIC_PUB, out);
  }
}
