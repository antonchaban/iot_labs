import logging
from typing import List
from fastapi import FastAPI
from redis import Redis
import paho.mqtt.client as mqtt

from app.adapters.store_api_adapter import StoreApiAdapter
from app.entities.processed_agent_data import ProcessedAgentData
from config import (
    STORE_API_BASE_URL,
    REDIS_HOST,
    REDIS_PORT,
    BATCH_SIZE,
    MQTT_TOPIC,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
)

# Configure logging settings
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)

# Create Redis client
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT)

# Create StoreApiAdapter instance
store_adapter = StoreApiAdapter(api_base_url=STORE_API_BASE_URL)

# FastAPI app
app = FastAPI()


@app.post("/processed_agent_data/")
async def save_processed_agent_data(processed_agent_data: ProcessedAgentData):
    logging.info("Received data via HTTP POST")
    redis_client.lpush("processed_agent_data", processed_agent_data.model_dump_json())

    processed_agent_data_batch: List[ProcessedAgentData] = []
    if redis_client.llen("processed_agent_data") >= BATCH_SIZE:
        for _ in range(BATCH_SIZE):
            item = redis_client.lpop("processed_agent_data")
            if item:
                parsed = ProcessedAgentData.model_validate_json(item)
                processed_agent_data_batch.append(parsed)

        store_adapter.save_data(processed_agent_data_batch=processed_agent_data_batch)

    return {"status": "ok"}


# MQTT client
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Failed to connect to MQTT broker with code: {rc}")


def on_message(client, userdata, msg):
    logging.info("Received data via MQTT")
    try:
        payload: str = msg.payload.decode("utf-8")
        processed_agent_data = ProcessedAgentData.model_validate_json(payload, strict=True)
        logging.info(f"Parsed data: {processed_agent_data}")
        redis_client.lpush("processed_agent_data", processed_agent_data.model_dump_json())

        processed_agent_data_batch: List[ProcessedAgentData] = []
        if redis_client.llen("processed_agent_data") >= BATCH_SIZE:
            for _ in range(BATCH_SIZE):
                item = redis_client.lpop("processed_agent_data")
                if item:
                    parsed = ProcessedAgentData.model_validate_json(item)
                    processed_agent_data_batch.append(parsed)

            store_adapter.save_data(processed_agent_data_batch=processed_agent_data_batch)

    except Exception as e:
        logging.error(f"Error processing MQTT message: {e}")


# Setup MQTT
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
client.loop_start()
