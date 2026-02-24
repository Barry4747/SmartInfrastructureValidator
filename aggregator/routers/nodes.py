from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import schemas
from crud import nodes as crud_nodes

router = APIRouter(prefix="/api/nodes", tags=["Network Nodes"])

@router.post("/", response_model=schemas.NetworkNodeResponse, status_code=201)
def register_node(node: schemas.NetworkNodeCreate, db: Session = Depends(get_db)):
    """Registers new station."""
    return crud_nodes.create_network_node(db=db, node=node)

@router.get("/", response_model=List[schemas.NetworkNodeResponse])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Returns list of all registered stations."""
    return crud_nodes.get_nodes(db, skip=skip, limit=limit)

@router.delete("/", status_code=200)
def delete_all_nodes(db: Session = Depends(get_db)):
    """Deletes all network nodes (and their cascading logs and alarms)."""
    deleted_count = crud_nodes.delete_all_nodes(db)
    return {"status": "success", "message": f"Deleted {deleted_count} nodes."}