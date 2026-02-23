import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from geoalchemy2 import Geometry
import enum
from database import Base
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2.functions import ST_X, ST_Y

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

    @hybrid_property
    def longitude(self):
        if hasattr(self, '_longitude'):
            return self._longitude
        if self.location is not None and hasattr(self.location, 'desc'):
            try:
                import struct
                wkb = bytes.fromhex(self.location.desc)
                endian = '<' if wkb[0] == 1 else '>'
                type_val = struct.unpack(f'{endian}I', wkb[1:5])[0]
                if type_val & 0x20000000:
                    return struct.unpack(f'{endian}dd', wkb[9:25])[0]
                else:
                    return struct.unpack(f'{endian}dd', wkb[5:21])[0]
            except Exception:
                pass
        return 0.0

    @longitude.setter
    def longitude(self, value):
        self._longitude = value

    @longitude.expression
    def longitude(cls):
        return ST_X(cls.location)

    @hybrid_property
    def latitude(self):
        if hasattr(self, '_latitude'):
            return self._latitude
        if self.location is not None and hasattr(self.location, 'desc'):
            try:
                import struct
                wkb = bytes.fromhex(self.location.desc)
                endian = '<' if wkb[0] == 1 else '>'
                type_val = struct.unpack(f'{endian}I', wkb[1:5])[0]
                if type_val & 0x20000000:
                    return struct.unpack(f'{endian}dd', wkb[9:25])[1]
                else:
                    return struct.unpack(f'{endian}dd', wkb[5:21])[1]
            except Exception:
                pass
        return 0.0

    @latitude.setter
    def latitude(self, value):
        self._latitude = value

    @latitude.expression
    def latitude(cls):
        return ST_Y(cls.location)

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