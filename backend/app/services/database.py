from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional
from app.models.schemas import DiagnosisRecord


class Database:
    client: AsyncIOMotorClient = None
    db = None
    connected: bool = False
    
    @classmethod
    async def connect(cls, uri: str):
        try:
            cls.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
            cls.db = cls.client.agrosentinel
            await cls.client.admin.command('ping')
            cls.connected = True
        except Exception:
            cls.connected = False
    
    @classmethod
    async def disconnect(cls):
        if cls.client:
            cls.client.close()
    
    @classmethod
    async def save_diagnosis(cls, record: DiagnosisRecord) -> str:
        if not cls.connected:
            return "demo_id"
        try:
            record_dict = record.model_dump()
            record_dict["created_at"] = datetime.utcnow()
            result = await cls.db.diagnoses.insert_one(record_dict)
            return str(result.inserted_id)
        except Exception:
            return "error_id"
    
    @classmethod
    async def get_user_history(cls, user_id: str, limit: int = 50) -> list:
        if not cls.connected:
            return []
        try:
            cursor = cls.db.diagnoses.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            for r in results:
                r["_id"] = str(r["_id"])
            return results
        except Exception:
            return []
    
    @classmethod
    async def get_location_history(
        cls, 
        latitude: float, 
        longitude: float, 
        radius_deg: float = 0.01
    ) -> list:
        if not cls.connected:
            return []
        try:
            cursor = cls.db.diagnoses.find({
                "location.latitude": {"$gte": latitude - radius_deg, "$lte": latitude + radius_deg},
                "location.longitude": {"$gte": longitude - radius_deg, "$lte": longitude + radius_deg}
            }).sort("created_at", -1).limit(100)
            results = await cursor.to_list(length=100)
            for r in results:
                r["_id"] = str(r["_id"])
            return results
        except Exception:
            return []
