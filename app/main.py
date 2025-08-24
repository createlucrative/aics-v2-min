"""
Main FastAPI application for Aquaponics Intelligent Control System (AICS).
"""

import os
from datetime import datetime
from typing import List, Union

from fastapi import FastAPI, Depends, HTTPException, Header, Request, Response
from sqlalchemy.orm import Session
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from . import models, schemas
from .database import get_db, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aquaponics Intelligent Control System (AICS)")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

API_KEY = os.getenv("AICS_INGEST_API_KEY")


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
        response = await call_next(request)
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    return response


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/sensors", response_model=schemas.Sensor)
def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    db_sensor = models.Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


@app.get("/sensors", response_model=List[schemas.Sensor])
def list_sensors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sensors = db.query(models.Sensor).offset(skip).limit(limit).all()
    return sensors


@app.post("/ingest")
def ingest_readings(
    readings: Union[schemas.ReadingCreate, List[schemas.ReadingCreate]],
    x_api_key: str = Header(None),
    db: Session = Depends(get_db)
):
    # API key check
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Normalize to list
    if not isinstance(readings, list):
        reading_list = [readings]
    else:
        reading_list = readings

    created = 0
    for reading in reading_list:
        data = reading.dict()
        db_reading = models.Reading(**data)
        if db_reading.timestamp is None:
            db_reading.timestamp = datetime.utcnow()
        db.add(db_reading)
        created += 1

    db.commit()
    return {"status": "success", "ingested": created}
