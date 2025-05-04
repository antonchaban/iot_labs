import json
import logging
from typing import List
import requests
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_api_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url.rstrip("/")
        self.endpoint = f"{self.api_base_url}/processed_agent_data"
        self.logger = logging.getLogger(__name__)

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]) -> bool:
        if not processed_agent_data_batch:
            self.logger.info("No data to send to Store API.")
            return False

        try:
            payload = [item.model_dump(mode="json") for item in processed_agent_data_batch]
            response = requests.post(self.endpoint, json=payload)

            if response.status_code == 200:
                self.logger.info("Successfully sent data to Store API.")
                return True
            else:
                self.logger.error(f"Failed to send data to Store API: {response.status_code} {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Exception occurred during save_data: {e}")
            return False
