# SQLAlchemy setup
import json
from datetime import datetime
from typing import Set, List

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Path
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, MetaData, Column, Table, Integer, String, Float, DateTime, insert, select, delete, \
    update
from sqlalchemy.orm import Session, sessionmaker

from config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
metadata = MetaData()
# Define the ProcessedAgentData table
processed_agent_data = Table("processed_agent_data",metadata,
Column("id", Integer, primary_key=True, index=True),
Column("road_state", String),
Column("x", Float),
Column("y", Float),
Column("z", Float),
Column("latitude", Float),
Column("longitude", Float),
Column("timestamp", DateTime),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


###

# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float

class GpsData(BaseModel):
    latitude: float
    longitude: float

class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator('timestamp', mode='before')
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).")

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData

# Database model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

# FastAPI app setup
app = FastAPI()

# WebSocket subscriptions
subscriptions: Set[WebSocket] = set()
# FastAPI WebSocket endpoint
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    subscriptions.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions.remove(websocket)

# Function to send data to subscribed users
async def send_data_to_subscribers(data):
    for websocket in subscriptions:
        await websocket.send_json(json.dumps(data))

# FastAPI CRUD endpoints
@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData], db: Session = Depends(get_db)):
    insert_values = [
        {
            "road_state": d.road_state,
            "x": d.agent_data.accelerometer.x,
            "y": d.agent_data.accelerometer.y,
            "z": d.agent_data.accelerometer.z,
            "latitude": d.agent_data.gps.latitude,
            "longitude": d.agent_data.gps.longitude,
            "timestamp": d.agent_data.timestamp,
        }
        for d in data
    ]
    db.execute(insert(processed_agent_data), insert_values)
    db.commit()
    return {"inserted": len(insert_values)}

@app.get("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def read_processed_agent_data(processed_agent_data_id: int, db: Session = Depends(get_db)):
    stmt = select(processed_agent_data).where(processed_agent_data.c.id == processed_agent_data_id)
    result = db.execute(stmt).first()
    if result:
        return dict(result._mapping)
    else:
        raise HTTPException(status_code=404, detail="Data not found")


@app.get("/processed_agent_data/", response_model=List[ProcessedAgentDataInDB])
def list_processed_agent_data(db: Session = Depends(get_db)):
    stmt = select(processed_agent_data)
    result = db.execute(stmt).fetchall()
    return [dict(row._mapping) for row in result]


@app.put("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData, db: Session = Depends(get_db)):
    stmt = (
        update(processed_agent_data)
        .where(processed_agent_data.c.id == processed_agent_data_id)
        .values(
            road_state=data.road_state,
            x=data.agent_data.accelerometer.x,
            y=data.agent_data.accelerometer.y,
            z=data.agent_data.accelerometer.z,
            latitude=data.agent_data.gps.latitude,
            longitude=data.agent_data.gps.longitude,
            timestamp=data.agent_data.timestamp,
        )
        .returning(processed_agent_data)
    )
    result = db.execute(stmt).first()
    db.commit()
    if result:
        return dict(result._mapping)
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@app.delete("/processed_agent_data/{processed_agent_data_id}", response_model=ProcessedAgentDataInDB)
def delete_processed_agent_data(processed_agent_data_id: int, db: Session = Depends(get_db)):
    stmt = (
        delete(processed_agent_data)
        .where(processed_agent_data.c.id == processed_agent_data_id)
        .returning(processed_agent_data)
    )
    result = db.execute(stmt).first()
    db.commit()
    if result:
        return dict(result._mapping)
    else:
        raise HTTPException(status_code=404, detail="Data not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)