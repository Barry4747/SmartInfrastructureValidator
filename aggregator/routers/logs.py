from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
import schemas
from crud import logs as crud_logs
from ws_manager import manager
    
router = APIRouter(prefix="/api/nodes", tags=["Telemetry & Logs"])

@router.post("/{node_id}/logs", response_model=schemas.NodeStatusLogResponse, status_code=201)
async def report_node_status(node_id: UUID, log: schemas.NodeStatusLogCreate, db: Session = Depends(get_db)):
    """Reports new node status."""
    created_log = crud_logs.create_node_log(db=db, node_id=node_id, log=log)
    
    # Check for alarm conditions
    alarms = []
    if log.cpu_temperature_c > 50.0:
        alarms.append(f"High CPU temp: {log.cpu_temperature_c}°C")
    if log.connected_users > 450:
        alarms.append(f"High traffic: {log.connected_users} users")
        
    for alarm_msg in alarms:
        await manager.broadcast_json({
            "type": "new_alarm",
            "node_id": str(node_id),
            "severity": "CRITICAL" if log.cpu_temperature_c > 53.0 else "WARNING",
            "description": alarm_msg,
            "timestamp": created_log.timestamp.isoformat() if hasattr(created_log, "timestamp") else None
        })
    
    await manager.broadcast_json({
        "type": "new_log",
        "node_id": str(node_id),
        "log": {
            "is_online": log.is_online,
            "cpu_temperature_c": log.cpu_temperature_c,
            "connected_users": log.connected_users,
            "current_throughput_mbps": log.current_throughput_mbps,
            "timestamp": created_log.timestamp.isoformat() if hasattr(created_log, "timestamp") else None
        }
    })
    
    return created_log