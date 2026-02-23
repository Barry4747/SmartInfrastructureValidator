import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from geoalchemy2 import Geometry
import enum
from database import Base

class NodeType(enum.Enum):
    BTS = "BTS"
    NodeB = "NodeB"
    eNodeB = "eNodeB"
    gNodeB = "gNodeB"
    ng_eNodeB = "ng_eNodeB"

class ComponentType(enum.Enum):
    ANTENA = "ANTENA"
    TRANSCEIVER = "TRANSCEIVER"
    COOLING_FAN = "COOLING_FAN"
    POWER_SUPPLY = "POWER_SUPPLY"

class Status(enum.Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"

class Severity(enum.Enum):
    WARNING = "WARNING"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"

class NetworkNode(Base):
    __tablename__ = "network_node"
    
    node_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_name = Column(String, nullable=False)
    topology_path = Column(String, nullable=False)  
    node_type = Column(SQLEnum(NodeType), nullable=False)
    ip_address = Column(String, nullable=False)
    max_throughput_mbps = Column(Integer, nullable=False)
    location = Column(Geometry('POINT'), nullable=False) 
    vendor_config = Column(JSONB, default={})            
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    logs = relationship("NodeStatusLog", back_populates="node")
    components = relationship("HardwareComponent", back_populates="node")
    alarms = relationship("ActiveAlarm", back_populates="node")

class NodeStatusLog(Base):
    __tablename__ = "node_status_log"

    timestamp = Column(DateTime(timezone=True), primary_key=True, default=lambda: datetime.now(timezone.utc))
    node_id = Column(UUID(as_uuid=True), ForeignKey("network_node.node_id"), primary_key=True)
    is_online = Column(Boolean, nullable=False)
    cpu_temperature_c = Column(Float, nullable=False)
    connected_users = Column(Integer, nullable=False)
    current_throughput_mbps = Column(Float, nullable=False)

    node = relationship("NetworkNode", back_populates="logs")

class HardwareComponent(Base):
    __tablename__ = "hardware_component"

    component_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("network_node.node_id"), nullable=False)
    component_type = Column(SQLEnum(ComponentType), nullable=False)
    status = Column(SQLEnum(Status), default=Status.OK)

    node = relationship("NetworkNode", back_populates="components")

class ActiveAlarm(Base):
    __tablename__ = "active_alarm"

    alarm_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("network_node.node_id"), nullable=False)
    component_id = Column(UUID(as_uuid=True), ForeignKey("hardware_component.component_id"), nullable=True)
    severity = Column(SQLEnum(Severity), nullable=False)
    description = Column(String, nullable=False)
    raised_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    cleared_at = Column(DateTime(timezone=True), nullable=True)

    node = relationship("NetworkNode", back_populates="alarms")