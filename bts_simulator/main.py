import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from config import settings
from schemas import NetworkNodeRegistration
from state import current_state
from client import aggregator_client

logging.basicConfig(level=logging.INFO)

async def telemetry_loop():
    """Background: infinite loop generating metrics every X seconds."""
    while True:
        await asyncio.sleep(settings.heartbeat_interval_sec)
        
        if aggregator_client.node_id:
            metrics = current_state.generate_metrics()
            await aggregator_client.send_telemetry(metrics)
            logging.info(f"Telemetry sent | Users: {metrics.connected_users} | Temp: {metrics.cpu_temperature_c}°C")

@asynccontextmanager
async def lifespan(app: FastAPI):
    registration_data = NetworkNodeRegistration(
        node_name=settings.simulator_name,
        topology_path=settings.topology_path,
        node_type=settings.node_type,
        ip_address=settings.ip_address,
        max_throughput_mbps=settings.max_throughput,
        latitude=settings.latitude,
        longitude=settings.longitude,
        vendor_config={"fault_port": settings.fault_port}
    )
    
    await aggregator_client.register(registration_data)
    
    task = asyncio.create_task(telemetry_loop())
    
    yield
    
    task.cancel()
    await aggregator_client.close()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BTS Simulator API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/fault/cooling")
async def inject_cooling_fault():
    """Injects cooling fault. Temperature will start rising drastically."""
    current_state.cooling_failed = True
    return {"status": "fault_injected", "message": "Fan broken! Temperature is rising."}

@app.post("/api/fault/fix")
async def fix_faults():
    """Fixes the node. Parameters return to normal."""
    current_state.cooling_failed = False
    current_state.current_temp = current_state.base_temp
    return {"status": "fixed", "message": "Node fixed. Parameters are returning to normal."}