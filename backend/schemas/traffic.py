"""
Pydantic Schemas for Request & Response Data Validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PredictionRequest(BaseModel):
    sensor_id: str = Field(default="SENSOR-101", description="Sensor Identifier")
    average_speed: float = Field(default=45.0, ge=0.0, le=200.0, description="Space mean speed in km/h")
    vehicle_count: int = Field(default=80, ge=0, le=1000, description="Vehicle count in interval")
    occupancy_rate: float = Field(default=28.5, ge=0.0, le=100.0, description="Road occupancy percentage")
    traffic_volume: Optional[int] = Field(default=960, ge=0, description="Estimated hourly flow volume")
    speed_limit: Optional[float] = Field(default=100.0, ge=20.0, le=140.0, description="Road segment speed limit")
    timestamp: Optional[str] = Field(default=None, description="Optional ISO timestamp")

class StreamToggleRequest(BaseModel):
    action: str = Field(default="toggle", description="'start', 'stop', or 'toggle'")

class StreamRateRequest(BaseModel):
    interval_seconds: float = Field(default=3.0, ge=0.5, le=30.0, description="Stream interval in seconds")

class IncidentInjectionRequest(BaseModel):
    sensor_id: str = Field(..., description="Target Sensor ID to simulate incident on")
    severity: float = Field(default=0.65, ge=0.1, le=0.95, description="Speed drop severity fraction (0.1 - 0.95)")
    duration_seconds: int = Field(default=60, ge=10, le=600, description="Incident duration in seconds")
