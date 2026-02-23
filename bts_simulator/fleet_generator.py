import asyncio
import random
import httpx
import logging
from uuid import UUID
from schemas import NetworkNodeRegistration, NodeTelemetryPayload, NodeType

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

AGGREGATOR_URL = "http://localhost:8000"
NUM_STATIONS = 50

class VirtualNode:
    def __init__(self, index: int):
        self.name = f"POL_SIM_NODE_{index:03d}"
        self.type = random.choice(list(NodeType))
        self.lat = 51.0 + random.uniform(-2.0, 2.0)
        self.lon = 19.0 + random.uniform(-2.0, 2.0)
        self.node_id: UUID | None = None
        
        self.connected_users = random.randint(10, 500)
        self.temp = random.uniform(35.0, 55.0)

    def generate_metrics(self) -> NodeTelemetryPayload:
        self.connected_users = max(0, self.connected_users + random.randint(-5, 5))
        self.temp = self.temp + random.uniform(-1.0, 1.0)
        throughput = min(10000.0, self.connected_users * random.uniform(1.5, 3.5))
        
        return NodeTelemetryPayload(
            is_online=True,
            cpu_temperature_c=round(self.temp, 2),
            connected_users=self.connected_users,
            current_throughput_mbps=round(throughput, 2)
        )

async def simulate_node(node: VirtualNode, client: httpx.AsyncClient):
    reg_data = NetworkNodeRegistration(
        node_name=node.name,
        topology_path=f"PL.REGION_{random.randint(1,5)}.{node.type.value}.{node.name}",
        node_type=node.type,
        ip_address=f"10.0.{random.randint(1,255)}.{random.randint(1,255)}",
        max_throughput_mbps=10000 if node.type == NodeType.gNodeB else 1000,
        latitude=node.lat,
        longitude=node.lon
    )
    
    try:
        response = await client.post("/api/nodes/", json=reg_data.model_dump())
        if response.status_code == 201:
            node.node_id = response.json()["node_id"]
            logging.info(f"[+] Zarejestrowano {node.name} ({node.type.value})")
    except Exception as e:
        logging.error(f"[-] Błąd rejestracji {node.name}: {e}")
        return

    while True:
        await asyncio.sleep(random.uniform(4.0, 6.0)) 
        
        if node.node_id:
            metrics = node.generate_metrics()
            try:
                await client.post(f"/api/nodes/{node.node_id}/logs", json=metrics.model_dump())
                logging.debug(f"[{node.name}] Wysłano logi.")
            except Exception:
                pass

async def main():
    logging.info(f"Startowanie generatora obciążenia dla {NUM_STATIONS} stacji bazowych...")
    
    nodes = [VirtualNode(i) for i in range(1, NUM_STATIONS + 1)]
    
    limits = httpx.Limits(max_keepalive_connections=100, max_connections=200)
    async with httpx.AsyncClient(base_url=AGGREGATOR_URL, limits=limits, timeout=10.0) as client:
        
        tasks = [simulate_node(node, client) for node in nodes]
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())