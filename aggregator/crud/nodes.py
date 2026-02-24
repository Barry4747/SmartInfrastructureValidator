from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
import models
import schemas

def create_network_node(db: Session, node: schemas.NetworkNodeCreate):
    point = WKTElement(f'POINT({node.longitude} {node.latitude})', srid=4326)
    
    db_node = models.NetworkNode(
        node_name=node.node_name,
        topology_path=node.topology_path,
        node_type=node.node_type,
        ip_address=node.ip_address,
        max_throughput_mbps=node.max_throughput_mbps,
        vendor_config=node.vendor_config,
        location=point
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)

    db_node.latitude = node.latitude
    db_node.longitude = node.longitude

    return db_node

def get_nodes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.NetworkNode).offset(skip).limit(limit).all()

def delete_all_nodes(db: Session):
    try:
        db.query(models.NodeStatusLog).delete()
        db.query(models.ActiveAlarm).delete()
        db.query(models.HardwareComponent).delete()
        
        nodes_deleted = db.query(models.NetworkNode).delete()
        db.commit()
        return nodes_deleted
    except Exception as e:
        db.rollback()
        raise e