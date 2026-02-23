from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import init_db
from routers import nodes, logs

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

app.include_router(nodes.router)
app.include_router(logs.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Smart Infrastructure Validator is running."}