from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

class NodeType(str, Enum):
    BTS = "BTS"
    NodeB = "NodeB"
    eNodeB = "eNodeB"
    gNodeB = "gNodeB"
    ng_eNodeB = "ng_eNodeB"

class AlarmSeverity(str, Enum):
    WARNING = "WARNING"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"

class NetworkNodeRegistration(BaseModel):
    node_name: str
    topology_path: str
    node_type: NodeType
    ip_address: str
    max_throughput_mbps: int
    latitude: float
    longitude: float
    vendor_config: Dict[str, Any] = Field(default_factory=dict)

class NodeTelemetryPayload(BaseModel):
    is_online: bool
    cpu_temperature_c: float
    connected_users: int
    current_throughput_mbps: float

class ActiveAlarmPayload(BaseModel):
    severity: AlarmSeverity
    description: str
    component_id: Optional[str] = None