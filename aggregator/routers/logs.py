from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
import schemas
from crud import logs as crud_logs

router = APIRouter(prefix="/api/nodes", tags=["Telemetry & Logs"])

@router.post("/{node_id}/logs", response_model=schemas.NodeStatusLogResponse, status_code=201)
def report_node_status(node_id: UUID, log: schemas.NodeStatusLogCreate, db: Session = Depends(get_db)):
    """Reports new node status."""
    return crud_logs.create_node_log(db=db, node_id=node_id, log=log)