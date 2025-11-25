"""
AgroSentinel Disease Data
Contains disease classes, remedies, and treatment information
"""

# Disease classes matching our trained model
DISEASE_CLASSES = [
    "pepper_bacterial_spot",
    "pepper_healthy",
    "potato_early_blight",
    "potato_healthy",
    "potato_late_blight",
    "tomato_bacterial_spot",
    "tomato_early_blight",
    "tomato_healthy",
    "tomato_late_blight",
    "tomato_leaf_mold",
    "tomato_mosaic_virus",
    "tomato_septoria_leaf_spot",
    "tomato_spider_mites",
    "tomato_target_spot",
    "tomato_yellow_leaf_curl_virus"
]

# Display names for UI
DISEASE_DISPLAY_NAMES = {
    "pepper_bacterial_spot": "Pepper Bacterial Spot",
    "pepper_healthy": "Pepper (Healthy)",
    "potato_early_blight": "Potato Early Blight",
    "potato_healthy": "Potato (Healthy)",
    "potato_late_blight": "Potato Late Blight",
    "tomato_bacterial_spot": "Tomato Bacterial Spot",
    "tomato_early_blight": "Tomato Early Blight",
    "tomato_healthy": "Tomato (Healthy)",
    "tomato_late_blight": "Tomato Late Blight",
    "tomato_leaf_mold": "Tomato Leaf Mold",
    "tomato_mosaic_virus": "Tomato Mosaic Virus",
    "tomato_septoria_leaf_spot": "Tomato Septoria Leaf Spot",
    "tomato_spider_mites": "Tomato Spider Mites",
    "tomato_target_spot": "Tomato Target Spot",
    "tomato_yellow_leaf_curl_virus": "Tomato Yellow Leaf Curl Virus"
}

# Severity levels for each disease
SEVERITY_LEVELS = {
    "pepper_bacterial_spot": "medium",
    "pepper_healthy": "none",
    "potato_early_blight": "high",
    "potato_healthy": "none",
    "potato_late_blight": "critical",
    "tomato_bacterial_spot": "medium",
    "tomato_early_blight": "high",
    "tomato_healthy": "none",
    "tomato_late_blight": "critical",
    "tomato_leaf_mold": "medium",
    "tomato_mosaic_virus": "high",
    "tomato_septoria_leaf_spot": "medium",
    "tomato_spider_mites": "medium",
    "tomato_target_spot": "medium",
    "tomato_yellow_leaf_curl_virus": "critical"
}

# Detailed remedies and treatment information
REMEDIES = {
    "pepper_bacterial_spot": {
        "spray": "Copper hydroxide @ 2g/L or Streptomycin sulphate @ 0.5g/L",
        "repeat": "7-10 days",
        "precautions": "Remove infected leaves, avoid overhead irrigation, use disease-free seeds",
        "organic": "Neem oil spray @ 5ml/L, copper-based organic fungicides",
        "severity": "medium",
        "yield_loss": "10-50% if untreated"
    },
    "pepper_healthy": {
        "spray": "No treatment needed",
        "repeat": "N/A",
        "precautions": "Continue good agricultural practices, maintain proper spacing",
        "organic": "Regular neem oil spray for prevention",
        "severity": "none",
        "yield_loss": "None"
    },
    "potato_early_blight": {
        "spray": "Mancozeb 75WP @ 2.5g/L or Chlorothalonil @ 2g/L",
        "repeat": "7-10 days",
        "precautions": "Crop rotation, remove infected debris, avoid excess nitrogen",
        "organic": "Copper fungicide, compost tea spray",
        "severity": "high",
        "yield_loss": "20-50% if untreated"
    },
    "potato_healthy": {
        "spray": "No treatment needed",
        "repeat": "N/A",
        "precautions": "Maintain proper hilling, balanced fertilization",
        "organic": "Mulching, companion planting",
        "severity": "none",
        "yield_loss": "None"
    },
    "potato_late_blight": {
        "spray": "Metalaxyl + Mancozeb @ 2.5g/L or Cymoxanil + Mancozeb @ 3g/L",
        "repeat": "5-7 days during outbreak",
        "precautions": "URGENT: Destroy infected plants immediately, avoid overhead irrigation",
        "organic": "Bordeaux mixture @ 1%, remove all infected material",
        "severity": "critical",
        "yield_loss": "Up to 100% - can destroy entire crop"
    },
    "tomato_bacterial_spot": {
        "spray": "Copper oxychloride @ 3g/L or Streptocycline @ 0.5g/L",
        "repeat": "7-10 days",
        "precautions": "Use certified seeds, avoid working with wet plants",
        "organic": "Copper-based sprays, remove infected plants",
        "severity": "medium",
        "yield_loss": "10-30% if untreated"
    },
    "tomato_early_blight": {
        "spray": "Mancozeb 75WP @ 2.5g/L or Azoxystrobin @ 1ml/L",
        "repeat": "7-10 days",
        "precautions": "Stake plants, mulch to prevent soil splash, remove lower leaves",
        "organic": "Neem oil + baking soda spray, compost tea",
        "severity": "high",
        "yield_loss": "20-40% if untreated"
    },
    "tomato_healthy": {
        "spray": "No treatment needed",
        "repeat": "N/A",
        "precautions": "Continue proper staking, pruning, and balanced nutrition",
        "organic": "Regular inspection, companion planting with basil",
        "severity": "none",
        "yield_loss": "None"
    },
    "tomato_late_blight": {
        "spray": "Metalaxyl-M + Mancozeb @ 2.5g/L or Dimethomorph @ 1g/L",
        "repeat": "5-7 days - URGENT treatment needed",
        "precautions": "CRITICAL: Remove and destroy infected plants, do not compost",
        "organic": "Bordeaux mixture @ 1%, immediately remove infected parts",
        "severity": "critical",
        "yield_loss": "Up to 100% - extremely destructive"
    },
    "tomato_leaf_mold": {
        "spray": "Carbendazim @ 1g/L or Chlorothalonil @ 2g/L",
        "repeat": "10-14 days",
        "precautions": "Improve ventilation, reduce humidity, space plants properly",
        "organic": "Baking soda spray @ 5g/L, improve air circulation",
        "severity": "medium",
        "yield_loss": "10-30% if untreated"
    },
    "tomato_mosaic_virus": {
        "spray": "No chemical cure - viral disease",
        "repeat": "N/A",
        "precautions": "Remove infected plants, disinfect tools, control aphids",
        "organic": "Milk spray (1:9 ratio) may reduce spread, remove infected plants",
        "severity": "high",
        "yield_loss": "20-70% depending on infection stage"
    },
    "tomato_septoria_leaf_spot": {
        "spray": "Mancozeb @ 2.5g/L or Copper hydroxide @ 2g/L",
        "repeat": "7-10 days",
        "precautions": "Remove infected leaves, mulch, avoid overhead watering",
        "organic": "Copper fungicide, neem oil spray",
        "severity": "medium",
        "yield_loss": "15-30% if untreated"
    },
    "tomato_spider_mites": {
        "spray": "Dicofol @ 2ml/L or Abamectin @ 0.5ml/L",
        "repeat": "7 days, 2-3 applications",
        "precautions": "Increase humidity, spray water on undersides of leaves",
        "organic": "Neem oil @ 5ml/L, insecticidal soap, predatory mites",
        "severity": "medium",
        "yield_loss": "10-25% if untreated"
    },
    "tomato_target_spot": {
        "spray": "Azoxystrobin @ 1ml/L or Chlorothalonil @ 2g/L",
        "repeat": "7-10 days",
        "precautions": "Improve air circulation, stake plants, remove debris",
        "organic": "Copper fungicide, proper plant spacing",
        "severity": "medium",
        "yield_loss": "15-35% if untreated"
    },
    "tomato_yellow_leaf_curl_virus": {
        "spray": "No chemical cure - control whitefly vectors with Imidacloprid @ 0.3ml/L",
        "repeat": "Whitefly control: 10-14 days",
        "precautions": "CRITICAL: Remove infected plants, use reflective mulch, insect-proof nets",
        "organic": "Yellow sticky traps, neem oil for whiteflies, remove infected plants",
        "severity": "critical",
        "yield_loss": "Up to 100% - no cure once infected"
    }
}


def get_disease_info(disease_class: str) -> dict:
    """Get comprehensive disease information"""
    display_name = DISEASE_DISPLAY_NAMES.get(disease_class, disease_class.replace("_", " ").title())
    severity = SEVERITY_LEVELS.get(disease_class, "unknown")
    remedy = REMEDIES.get(disease_class, {
        "spray": "Consult local agricultural extension office",
        "repeat": "As recommended",
        "precautions": "Remove infected plant material",
        "organic": "Neem oil spray as general treatment",
        "severity": severity,
        "yield_loss": "Variable"
    })
    
    # Determine if it's a healthy plant
    is_healthy = "healthy" in disease_class.lower()
    
    # Extract crop type
    crop = disease_class.split("_")[0].capitalize()
    
    return {
        "class_name": disease_class,
        "display_name": display_name,
        "crop": crop,
        "is_healthy": is_healthy,
        "severity": severity,
        "treatment": {
            "chemical": remedy.get("spray", ""),
            "application_interval": remedy.get("repeat", ""),
            "precautions": remedy.get("precautions", ""),
            "organic_alternative": remedy.get("organic", ""),
            "potential_yield_loss": remedy.get("yield_loss", "")
        }
    }


def get_all_diseases() -> list:
    """Get list of all diseases with info"""
    return [get_disease_info(d) for d in DISEASE_CLASSES]
