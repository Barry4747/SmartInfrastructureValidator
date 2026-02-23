from sqlalchemy.orm import Session
import models
import schemas
from uuid import UUID

def create_node_log(db: Session, node_id: UUID, log: schemas.NodeStatusLogCreate):
    db_log = models.NodeStatusLog(
        node_id=node_id,
        is_online=log.is_online,
        cpu_temperature_c=log.cpu_temperature_c,
        connected_users=log.connected_users,
        current_throughput_mbps=log.current_throughput_mbps
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log