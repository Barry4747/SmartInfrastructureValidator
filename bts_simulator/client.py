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
        try:
            logger.info(f"Registration in Aggregator: {self.base_url}")
            response = await self.client.post("/api/nodes/", json=payload.model_dump())
            response.raise_for_status()
            
            data = response.json()
            self.node_id = data["node_id"]
            logger.info(f"Successfully registered! Received ID: {self.node_id}")
            return self.node_id
        except Exception as e:
            logger.error(f"Error registering in Aggregator: {e}")
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