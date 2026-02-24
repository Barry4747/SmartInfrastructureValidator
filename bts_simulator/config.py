from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    aggregator_url: str = Field(default="http://network_aggregator:8000")
    
    simulator_name: str = Field(default="WRO_5G_SIM_01")
    node_type: str = Field(default="gNodeB")
    ip_address: str = Field(default="127.0.0.1")
    max_throughput: int = Field(default=10000)
    latitude: float = Field(default=51.107883)
    longitude: float = Field(default=17.038538)
    topology_path: str = Field(default="PL.WRO.SIM.gNodeB_01")
    fault_port: int = Field(default=8001)
    
    heartbeat_interval_sec: int = Field(default=5)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()