import requests
import logging
import threading
import time

logger = logging.getLogger("CloudSync")

CLOUD_URL = "http://localhost:8000/api/telemetry" # Change in production
sync_queue = []
queue_lock = threading.Lock()

def push_to_cloud(payload: dict):
    with queue_lock:
        sync_queue.append(payload)

def sync_worker():
    while True:
        payloads_to_send = []
        with queue_lock:
            if sync_queue:
                # Batch up to 10 payloads
                payloads_to_send = sync_queue[:10]
                del sync_queue[:10]
        
        for payload in payloads_to_send:
            try:
                response = requests.post(CLOUD_URL, json=payload, timeout=5)
                if response.status_code == 200:
                    logger.info(f"Successfully synced {payload.get('device_id')} to cloud.")
                else:
                    logger.error(f"Cloud sync failed with status {response.status_code}")
                    # Re-queue on failure
                    with queue_lock:
                        sync_queue.insert(0, payload)
            except Exception as e:
                logger.error(f"Cloud sync exception: {e}")
                # Re-queue on failure
                with queue_lock:
                    sync_queue.insert(0, payload)
        
        time.sleep(5) # Sync interval

def start_sync():
    thread = threading.Thread(target=sync_worker, daemon=True)
    thread.start()
    logger.info("Cloud synchronization worker started.")
