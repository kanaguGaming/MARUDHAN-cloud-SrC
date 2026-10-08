import time
import logging
from local_broker import start_mqtt
from cloud_sync import start_sync

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MFCU_Main")

def main():
    logger.info("Starting Marudhan Farm Control Unit (MFCU)...")
    
    # 1. Start Cloud Synchronization Worker
    start_sync()
    
    # 2. Start Local MQTT Broker Connection
    start_mqtt()
    
    logger.info("MFCU is running. Press Ctrl+C to exit.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down MFCU...")

if __name__ == "__main__":
    main()
