from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from models import NodeType, ComponentType, Status, Severity

class NetworkNodeBase(BaseModel):
    node_name: str
    topology_path: str
    node_type: NodeType
    ip_address: str
    max_throughput_mbps: int
    vendor_config: Dict[str, Any] = Field(default_factory=dict)
    # For API simplicity, coordinates are taken as floats, 
    # and will be converted to PostGIS geometry in the business logic
    latitude: float
    longitude: float 

class NetworkNodeCreate(NetworkNodeBase):
    pass

class NetworkNodeResponse(NetworkNodeBase):
    node_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NodeStatusLogCreate(BaseModel):
    is_online: bool
    cpu_temperature_c: float
    connected_users: int
    current_throughput_mbps: float

class NodeStatusLogResponse(NodeStatusLogCreate):
    timestamp: datetime
    node_id: UUID

    model_config = ConfigDict(from_attributes=True)

class ActiveAlarmCreate(BaseModel):
    component_id: Optional[UUID] = None
    severity: Severity
    description: str

class ActiveAlarmResponse(ActiveAlarmCreate):
    alarm_id: UUID
    node_id: UUID
    raised_at: datetime
    cleared_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)