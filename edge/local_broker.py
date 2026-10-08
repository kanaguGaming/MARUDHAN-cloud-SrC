import paho.mqtt.client as mqtt
import json
import logging
from aaru_rules import evaluate_telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LocalBroker")

BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC_TELEMETRY = "marudhan/device/+/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to local MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_TELEMETRY)
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        logger.info(f"Received telemetry on {msg.topic}: {payload}")
        
        # 1. Evaluate local rules (AARU)
        evaluate_telemetry(payload)
        
        # 2. Push to cloud sync queue (to be implemented in cloud_sync)
        from cloud_sync import push_to_cloud
        push_to_cloud(payload)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def start_mqtt():
    client = mqtt.Client(client_id="MFCU_Gateway")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        client.loop_start()
    except Exception as e:
        logger.error(f"MQTT Connection failed: {e}")
