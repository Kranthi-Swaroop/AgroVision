from app.models.schemas import WeatherData
from app.services.disease_data import SEVERITY_LEVELS

# Healthy classes based on our model
HEALTHY_CLASSES = ["pepper_healthy", "potato_healthy", "tomato_healthy"]

# Risk thresholds for different disease types
RISK_THRESHOLDS = {
    "pepper_bacterial_spot": {"humidity": 70, "temp_min": 20, "temp_max": 35},
    "potato_early_blight": {"humidity": 60, "temp_min": 20, "temp_max": 30},
    "potato_late_blight": {"humidity": 80, "temp_min": 10, "temp_max": 25},
    "tomato_bacterial_spot": {"humidity": 70, "temp_min": 20, "temp_max": 35},
    "tomato_early_blight": {"humidity": 60, "temp_min": 20, "temp_max": 30},
    "tomato_late_blight": {"humidity": 85, "temp_min": 10, "temp_max": 25},
    "tomato_leaf_mold": {"humidity": 85, "temp_min": 15, "temp_max": 25},
    "tomato_mosaic_virus": {"humidity": 50, "temp_min": 20, "temp_max": 35},
    "tomato_septoria_leaf_spot": {"humidity": 75, "temp_min": 15, "temp_max": 25},
    "tomato_spider_mites": {"humidity": 40, "temp_min": 25, "temp_max": 40},
    "tomato_target_spot": {"humidity": 80, "temp_min": 20, "temp_max": 30},
    "tomato_yellow_leaf_curl_virus": {"humidity": 50, "temp_min": 25, "temp_max": 35},
}


class RiskEngine:
    @staticmethod
    def calculate_risk(disease: str, confidence: float, weather: WeatherData) -> tuple[float, str]:
        if disease in HEALTHY_CLASSES:
            return 0.0, "HEALTHY"
        
        thresholds = RISK_THRESHOLDS.get(disease)
        if not thresholds:
            return confidence * 0.5, "UNKNOWN"
        
        risk_factors = 0
        total_factors = 3
        
        if weather.humidity >= thresholds["humidity"]:
            risk_factors += 1
        
        if thresholds["temp_min"] <= weather.temperature <= thresholds["temp_max"]:
            risk_factors += 1
        
        if weather.humidity > 85 or "rain" in weather.description.lower():
            risk_factors += 1
        
        environmental_risk = risk_factors / total_factors
        combined_risk = (confidence * 0.6) + (environmental_risk * 0.4)
        
        if combined_risk >= 0.8:
            level = "CRITICAL"
        elif combined_risk >= 0.6:
            level = "HIGH"
        elif combined_risk >= 0.4:
            level = "MODERATE"
        else:
            level = "LOW"
        
        return round(combined_risk, 3), level
