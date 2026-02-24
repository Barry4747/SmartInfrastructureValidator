import asyncio
import httpx
import logging
from config import settings
from schemas import NetworkNodeRegistration, NodeTelemetryPayload

logger = logging.getLogger("aggregator_client")
logger.setLevel(logging.INFO)

class AggregatorClient:
    def __init__(self):
        self.base_url = settings.aggregator_url
        self.node_id = None
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def register(self, payload: NetworkNodeRegistration):
        max_retries = 10
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Registration in Aggregator (attempt {attempt+1}/{max_retries}): {self.base_url}")
                response = await self.client.post("/api/nodes/", json=payload.model_dump())
                response.raise_for_status()
                
                data = response.json()
                self.node_id = data["node_id"]
                logger.info(f"Successfully registered! Received ID: {self.node_id}")
                return self.node_id
            except (httpx.ConnectError, httpx.HTTPStatusError, Exception) as e:
                logger.warning(f"Error registering in Aggregator: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Could not register.")
                    return None

    async def send_telemetry(self, payload: NodeTelemetryPayload):
        if not self.node_id:
            return
        try:
            await self.client.post(f"/api/nodes/{self.node_id}/logs", json=payload.model_dump())
            logger.debug(f"Telemetry sent. Temp: {payload.cpu_temperature_c}°C")
        except Exception as e:
            logger.error(f"Error sending telemetry: {e}")

    async def close(self):
        await self.client.aclose()

aggregator_client = AggregatorClient()