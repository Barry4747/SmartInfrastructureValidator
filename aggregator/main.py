import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import nodes, logs
from ws_manager import manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Database init")
    init_db()
    print("Database ready")
    yield
    print("Closing connections")

app = FastAPI(
    title="Smart Infrastructure Validator API",
    description="Centralized Aggregator of telecommunication metrics 5G/4G",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nodes.router)
app.include_router(logs.router)

@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Smart Infrastructure Validator is running."}