"""
Pydantic schemas for API input and output models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ReadingCreate(BaseModel):
    sensor_id: int
    metric: str
    value: float
    timestamp: Optional[datetime] = None


class Reading(BaseModel):
    id: int
    sensor_id: int
    metric: str
    value: float
    timestamp: datetime

    class Config:
        orm_mode = True


class SensorCreate(BaseModel):
    name: str
    metric: str
    unit: str
    location: Optional[str] = None


class Sensor(BaseModel):
    id: int
    name: str
    metric: str
    unit: str
    location: Optional[str] = None
    readings: List[Reading] = []

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None


class Recipe(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
