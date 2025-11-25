from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from app.config import get_settings
from app.services.inference import get_inference
from app.services.weather_service import WeatherService
from app.services.risk_engine import RiskEngine
from app.services.database import Database
from app.services.disease_data import REMEDIES, DISEASE_CLASSES, get_disease_info
from app.services.translations import get_disease_name, get_risk_level_name, get_supported_languages
from app.models.schemas import Location, DiagnosisRecord, RiskAnalysis

router = APIRouter(prefix="/api", tags=["diagnosis"])
settings = get_settings()

# Healthy classes based on our model
HEALTHY_CLASSES = ["pepper_healthy", "potato_healthy", "tomato_healthy"]


@router.get("/languages")
async def get_languages():
    """Get list of supported languages"""
    return {"languages": get_supported_languages()}


@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    lang: str = Query("en", description="Language code (en, hi, te, ta, kn)")
):
    try:
        # Check content type with fallback
        content_type = file.content_type or ""
        if content_type and not content_type.startswith("image/"):
            # Try to detect from filename
            filename = file.filename or ""
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                raise HTTPException(400, "File must be an image")
        
        image_bytes = await file.read()
        inference = get_inference(settings.model_path)
        disease, confidence, top_predictions, is_confident = inference.predict(image_bytes)
        
        disease_info = get_disease_info(disease)
        
        # Build response
        response = {
            "disease": disease,
            "display_name": get_disease_name(disease, lang),
            "confidence": confidence,
            "crop": disease_info["crop"],
            "is_healthy": disease_info["is_healthy"],
            "severity": disease_info["severity"],
            "top_predictions": top_predictions[:3] if top_predictions else [],
            "is_confident": is_confident
        }
        
        # Add warning if not confident
        if not is_confident:
            response["warning"] = "Low confidence prediction. The image may not be a clear plant leaf or the disease might not be in our database."
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Prediction error: {str(e)}")


@router.post("/analyze")
async def analyze_with_risk(
    file: UploadFile = File(...),
    latitude: float = Query(...),
    longitude: float = Query(...),
    lang: str = Query("en", description="Language code (en, hi, te, ta, kn)")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
    image_bytes = await file.read()
    inference = get_inference(settings.model_path)
    disease, confidence, top_predictions, is_confident = inference.predict(image_bytes)
    
    disease_info = get_disease_info(disease)
    
    weather_service = WeatherService(settings.openweathermap_api_key)
    weather = await weather_service.get_weather(latitude, longitude)
    
    risk_score, risk_level = RiskEngine.calculate_risk(disease, confidence, weather)
    
    remedy = REMEDIES.get(disease, {
        "spray": "Consult local agricultural officer",
        "repeat": "N/A",
        "precautions": "Monitor crop closely"
    })
    
    record = DiagnosisRecord(
        location=Location(latitude=latitude, longitude=longitude),
        disease=disease,
        confidence=confidence,
        weather=weather,
        risk_score=risk_score,
        remedy=remedy
    )
    await Database.save_diagnosis(record)
    
    return {
        "disease": disease,
        "display_name": get_disease_name(disease, lang),
        "confidence": confidence,
        "crop": disease_info["crop"],
        "is_healthy": disease_info["is_healthy"],
        "severity": disease_info["severity"],
        "weather": weather,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_level_display": get_risk_level_name(risk_level, lang),
        "treatment": disease_info["treatment"],
        "remedy": remedy,
        "is_confident": is_confident,
        "warning": None if is_confident else "Low confidence prediction. Results may be inaccurate."
    }


@router.get("/weather")
async def get_weather(latitude: float = Query(...), longitude: float = Query(...)):
    weather_service = WeatherService(settings.openweathermap_api_key)
    return await weather_service.get_weather(latitude, longitude)


@router.get("/history/user/{user_id}")
async def get_user_history(user_id: str, limit: int = Query(50, le=100)):
    return await Database.get_user_history(user_id, limit)


@router.get("/history/location")
async def get_location_history(
    latitude: float = Query(...),
    longitude: float = Query(...)
):
    return await Database.get_location_history(latitude, longitude)


@router.get("/remedies/{disease}")
async def get_remedy(disease: str):
    remedy = REMEDIES.get(disease)
    if not remedy:
        raise HTTPException(404, "Disease not found")
    return {"disease": disease, "remedy": remedy}
