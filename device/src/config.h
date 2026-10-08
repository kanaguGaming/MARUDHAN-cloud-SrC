#ifndef CONFIG_H
#define CONFIG_H

// WiFi Config
#define WIFI_SSID "MARUDHAN_FARM_NETWORK"
#define WIFI_PASSWORD "marudhan123"

// MQTT Config
#define MQTT_BROKER "192.168.1.100" // Replace with MFCU Raspberry Pi IP
#define MQTT_PORT 1883
#define MQTT_CLIENT_ID "ESP32_MANN_01"
#define MQTT_TOPIC_PUB "marudhan/device/mann/telemetry"
#define MQTT_TOPIC_SUB "marudhan/device/mann/command"

// Sensor Config
#define SOIL_MOISTURE_PIN 34 // ADC1_CH6

#endif
