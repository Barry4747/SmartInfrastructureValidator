import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS ltree;"))
    
    Base.metadata.create_all(bind=engine)
    
    with engine.begin() as conn:
        conn.execute(text("""
            SELECT create_hypertable('node_status_log', by_range('timestamp'), if_not_exists => TRUE);
        """))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()