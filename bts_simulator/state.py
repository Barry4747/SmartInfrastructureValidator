import random
from schemas import NodeTelemetryPayload

class NodeState:
    def __init__(self):
        self.is_online = True
        self.cooling_failed = False
        self.base_temp = 45.0
        self.current_temp = 45.0
        self.connected_users = 100
        self.max_throughput = 1000.0

    def generate_metrics(self) -> NodeTelemetryPayload:
        self.connected_users = max(0, self.connected_users + random.randint(-10, 15))
        
        throughput = min(self.max_throughput, self.connected_users * random.uniform(2.0, 5.0))
        
        if self.cooling_failed:
            self.current_temp = min(95.0, self.current_temp + random.uniform(2.0, 6.0))
        else:
            self.current_temp = self.base_temp + random.uniform(-2.0, 2.0)

        return NodeTelemetryPayload(
            is_online=self.is_online,
            cpu_temperature_c=round(self.current_temp, 2),
            connected_users=self.connected_users,
            current_throughput_mbps=round(throughput, 2)
        )

current_state = NodeState()