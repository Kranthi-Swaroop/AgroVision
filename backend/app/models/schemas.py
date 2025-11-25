from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Location(BaseModel):
    latitude: float
    longitude: float


class WeatherData(BaseModel):
    humidity: int
    temperature: float
    description: str
    wind_speed: float


class PredictionResult(BaseModel):
    disease: str
    confidence: float
    bounding_boxes: list


class RiskAnalysis(BaseModel):
    disease: str
    confidence: float
    weather: WeatherData
    risk_score: float
    risk_level: str
    remedy: dict


class DiagnosisRecord(BaseModel):
    user_id: Optional[str] = None
    location: Location
    disease: str
    confidence: float
    weather: WeatherData
    risk_score: float
    remedy: dict
    image_url: Optional[str] = None
    created_at: datetime = None
